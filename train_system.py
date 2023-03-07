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
    
    
    def Wait(self, train, epoch):
        max_wait =  self.start_time[train] - self.time
        if epoch > max_wait:
            self.Load(train, epoch - max_wait)
        
     
    def Load(self,train,effective_epoch):
        self.states[train].state = states.LOADING
        if(effective_epoch>0):
            station=self.states[train].station
            potential_load = min(effective_epoch/ self.gen.beta[station], self.gen.lmax - self.load[train])
            self.load[train] += min(potential_load , self.platform[station])
            if potential_load < self.platform[station]:
                self.platform[station] -= potential_load
                if self.load[train] == self.gen.lmax:
                    loading_time=(potential_load * self.gen.beta[station])
                    self.Move(train, effective_epoch - loading_time)
            else:
                loading_time = (self.platform[station] * self.gen.beta[station])
                self.platform[station] = 0
                self.Move(train,effective_epoch - loading_time)
        
                
    def Unload(self,train,effective_epoch):
        self.states[train].state = states.UNLOADING #maybe it should be outside, think about it later
        if(effective_epoch>0):
            station = self.states[train].station
            potential_unload = effective_epoch / self.gen.alpha[station]
            max_unload = self.load[train] - self.load_before_alight[train] * (1 - self.gen.eta[train, station])
            self.load[train] = min(potential_unload, max_unload)
            if potential_unload >= max_unload:
                self.Load(train,effective_epoch - max_unload * self.gen.alpha[station])
                
    
    def Move(self,train,effective_epoch):
        self.states[train].state = states.MOVING
        if(effective_epoch>0):
            potential_move = effective_epoch * self.gen.speed_kmh / units.hour
            max_move = (10 - (self.location[train]) % 10)
            moving_distance = min(potential_move,max_move) * self.gen.speed_kmh / units.hour
            moving_time = (moving_distance / self.gen.speed_kmh) * units.hour
            self.location[train] += moving_distance
            if potential_move >= max_move:
                self.states[train].station += 1
                self.load_before_alight[train] = self.load[train]
                self.Unload(train,effective_epoch-moving_time)
                
    def advance(self , epoch = 60 , noise = 0):
        self.time = self.time + epoch
        for i in range(self.gen.stations):
            self.platform[i] = self.platform[i] + (self.gen.lambda_[i] + noise * random.uniform(-0.3,20)) * epoch
        for train in range(self.gen.trains):
            # CASE 0 - Finished
            if (self.states[train].state == states.MOVING and self.states[train].station == self.gen.stations - 1):
                self.states[train].state = states.FINISHED
            elif (self.states[train].state == states.WAITING_FOR_FIRST_DEPART):
                self.Wait(train,epoch)
            # CASE 2 - loading
            elif (self.states[train].state == states.LOADING):
                self.Load(train,epoch)
            # CASE 3 - Unloading
            elif self.states[train].state == states.UNLOADING:
                self.Unload(train,epoch)
            # CASE 4 - Moving
            elif self.states[train].state == states.MOVING:
                self.Move(train,epoch)
                


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
        epoch = 10
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
