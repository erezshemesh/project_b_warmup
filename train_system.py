from generator import *
import random


class TrainSystem:

    def __init__(self, T, L, P, gen: Generator):
        self.T = T
        self.L = L
        self.P = P
        self.gen = gen
        self.time = 21600  # 6:00AM
        self.location = np.zeros(gen.trains)
        self.states = []
        for _ in range(self.gen.trains):
            self.states += [TrainState()]
        self.load = np.zeros(gen.trains)
        self.load_before_alight = np.zeros(gen.trains)
        self.platform = np.zeros(gen.stations)
        self.agent_speed = np.zeros(gen.trains)
        self.start_time = [T[train, 0] - L[train, 0] * self.gen.beta[0] for train in range(self.gen.trains)]

    def reset(self):
        self.time = 21600  # 6:00AM
        self.location = np.zeros(gen.trains)
        self.states = []
        for _ in range(self.gen.trains):
            self.states += [TrainState()]
        self.load = np.zeros(gen.trains)
        self.load_before_alight = np.zeros(gen.trains)
        self.platform = np.zeros(gen.stations)
        self.agent_speed = np.zeros(gen.trains)

    def advance(self , epoch = 60 , noise = 0):
        self.time = self.time + epoch
        for i in range(self.gen.stations):
            self.platform[i] = self.platform[i] + (self.gen.lambda_[i] + noise * random.uniform(-0.3,20)) * epoch
        for train in range(self.gen.trains):
            # CASE 0 - finished
            if (self.states[train].state == states.MOVING and self.states[train].station == self.gen.stations - 1):
                self.states[train].state = states.FINISHED
            # CASE 1 - initial
            elif (self.states[train].state == states.WAITING_FOR_FIRST_DEPART) and (self.start_time[train] < self.time):
                self.states[train].state = states.LOADING
                potential_load = min((self.time - self.start_time[train]) / self.gen.beta[0],
                                     self.gen.lmax - self.load[train])
                if potential_load < self.platform[0]:
                    self.load[train] = potential_load
                    self.platform[0] = self.platform[0] - potential_load
                else:
                    self.load = self.platform[0]
                    self.states[train].state = states.MOVING
                    self.location[train] = (epoch - (self.platform[0] * self.gen.beta[0])) * self.gen.speed_kmh / 3600
                    self.platform[0] = 0
            # CASE 2 - loading
            elif self.states[train].state == states.LOADING:
                s = self.states[train].station
                potential_load = min(epoch / self.gen.beta[s], self.gen.lmax - self.load[train])
                if potential_load < self.platform[s]:
                    self.load[train] = self.load[train] + potential_load
                    self.platform[s] = self.platform[s] - potential_load
                    if self.load[train] == self.gen.lmax:
                        self.states[train].state = states.MOVING
                        self.location[train] = self.location[train] +(
                                epoch - (potential_load * self.gen.beta[s])) * self.gen.speed_kmh / 3600

                else:
                    self.load[train] = self.load[train] + self.platform[s]
                    self.states[train].state = states.MOVING
                    self.location[train] = self.location[train] + (
                                epoch - (self.platform[s] * self.gen.beta[s])) * self.gen.speed_kmh / 3600
                    self.platform[s] = 0
            # CASE 3 - unloading
            elif self.states[train].state == states.UNLOADING:
                s = self.states[train].station
                potential_unload = epoch / self.gen.alpha[s]
                if self.load[train] - potential_unload > self.load_before_alight[train] * (1 - self.gen.eta[train, s]):
                    self.load[train] = self.load[train] - potential_unload
                else:
                    unloading_time = (self.load[train] - (
                                self.load_before_alight[train] * (1 - self.gen.eta[train, s]))) * self.gen.alpha[s]
                    self.load[train] = self.load_before_alight[train] * (1 - self.gen.eta[train, s])
                    self.states[train].state = states.LOADING
                    potential_load = min((epoch - unloading_time) / self.gen.beta[s], self.gen.lmax - self.load[train])
                    if potential_load < self.platform[s]:
                        self.load[train] = self.load[train] + potential_load
                        self.platform[s] = self.platform[s] - potential_load
                        if self.load[train] == self.gen.lmax:
                            self.states[train].state = states.MOVING
                            self.location[train] = self.location[train] + (
                                    epoch - (potential_load * self.gen.beta[s])) * self.gen.speed_kmh / 3600
                    else:
                        self.load[train] = self.load[train] + self.platform[s]
                        self.states[train].state = states.MOVING
                        self.location[train] = self.location[train] + (
                                    epoch - (self.platform[s] * self.gen.beta[s])) * self.gen.speed_kmh / 3600
                        self.platform[s] = 0
            # CASE 4 - MOVING
            elif self.states[train].state == states.MOVING:
                potential_move = epoch * self.gen.speed_kmh / 3600
                if potential_move < (10 - (self.location[train]) % 10):
                    self.location[train] = self.location[train] + potential_move
                else:
                    moving_time = ((10 - (self.location[train]) % 10) / self.gen.speed_kmh) * 3600
                    self.location[train] = self.location[train] + 10 - (self.location[train]) % 10
                    self.states[train].state = states.UNLOADING
                    self.load_before_alight[train] = self.load[train]
                    self.states[train].station = self.states[train].station + 1
                    s = self.states[train].station
                    potential_unload = (epoch - moving_time) / self.gen.alpha[s]
                    if potential_unload < self.load_before_alight[train] * self.gen.eta[train, s]:
                        self.load[train] = self.load[train] - potential_unload
                    else:
                        unloading_time = (self.load_before_alight[train] * self.gen.eta[train, s]) * self.gen.alpha[s]
                        self.load[train] = self.load_before_alight[train] * (1 - self.gen.eta[train, s])
                        self.states[train].state = states.LOADING
                        potential_load = min((epoch - unloading_time - moving_time) / self.gen.beta[s],
                                             self.gen.lmax - self.load[train])
                        if potential_load < self.platform[s]:
                            self.load[train] = self.load[train] + potential_load
                            self.platform[s] = self.platform[s] - potential_load
                            if self.load[train] == self.gen.lmax:
                                self.states[train].state = states.MOVING
                                self.location[train] = self.location[train] + (
                                        epoch - (potential_load * self.gen.beta[s])) * self.gen.speed_kmh / 3600
                        else:
                            self.load[train] = self.load[train] + self.platform[s]
                            self.states[train].state = states.MOVING
                            self.location[train] = self.location[train] + (epoch - (self.platform[s] * self.gen.beta[s])) * self.gen.speed_kmh / 3600
                            self.platform[s] = 


T = np.array([[43826, 47386, 50546, 53706],
              [51705, 53733, 57207, 60457],
              [62198, 64190, 66237, 69427],
              [76162, 78775, 81833, 85136],
              [82467, 83638, 84646, 85316],
              [84575, 85199, 85799, 86390]])

L = np.array([[6668, 10000, 10000, 10000],
              [2363, 4879, 9249, 10000],
              [3147, 5025, 5724, 8792],
              [4189, 6889, 8812, 9999],
              [1891, 2593, 2400, 1494],
              [632, 847, 854, 834]])

P = np.array([[6668, 7556, 8324, 9092],
              [2363, 3460, 6322, 7117],
              [3147, 3137, 2708, 5358],
              [4189, 4375, 4678, 4712],
              [1891, 1458, 843, 53],
              [632, 468, 345, 322]])

gen = Generator(
    trains=6,
    stations=4,
    t_alight_per_person=3,
    t_board_per_person=4,
    platform_arrivals_per_t=0.3,
    alight_fraction=0.4,
    number_of_carts=10,
    km_between_stations=10,
    speed_kmh=100,
    stop_t=10,
    tmin=180,
    train_capacity=10000,
    platform_capacity=100000,
    var=0
)

sys = TrainSystem(T, L, P, gen)
noise = False
for i in range(1):
    x = 0
    for t in range(600000):
        epoch = 200
        train = 1
        a = sys.states[train].state
        st = "WAITING FOR FIRST DEPART" if a == 0 else (
            "UNLOADING" if a == 1 else (
                "LOADING" if a == 2 else ("MOVING" if a == 3 else ("FINISHED" if a == 4 else "ERROR"))))
        if (st == "MOVING" and x == sys.states[train].station) or True:
            print(t, ": time: ", sys.time, ", location: ", int(sys.location[train]), ", load: ", int(sys.load[train]),
                  f", platform{sys.states[train].station}: ",
                  int(sys.platform[sys.states[train].station]), ", state: ", st, ", station: ",
                  sys.states[train].station)
            x = x + 1
        if st != "FINISHED":
            sys.advance(epoch , noise)
        else:
            print("DONE")
            break;
    sys.reset()
    noise = True
