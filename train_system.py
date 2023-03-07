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
        
        
        
    def loadFunc(self,train,station,potential_load,shift):   
        if potential_load < self.platform[station]:
            self.load[train] = self.load[train] + potential_load
            self.platform[station] = self.platform[station] - potential_load
            if self.load[train] == self.gen.lmax:
                self.states[train].state = states.MOVING
                self.location[train] = self.location[train] +((epoch-shift) - (potential_load * self.gen.beta[station])) * self.gen.speed_kmh / 3600
        else:
            self.load[train] = self.load[train] + self.platform[station]
            self.platform[station] = 0
            self.states[train].state = states.MOVING
            self.location[train] = self.location[train] + ((epoch-shift) - (self.platform[station] * self.gen.beta[station])) * self.gen.speed_kmh / 3600

    def advance(self , epoch = 60 , noise = 0):
        self.time = self.time + epoch
        for i in range(self.gen.stations):
            self.platform[i] = self.platform[i] + (self.gen.lambda_[i] + noise * random.uniform(-0.3,20)) * epoch
        for train in range(self.gen.trains):
            
            # curr_state=self.states[train].state
            # curr_station=self.states[train].station
            
            # match curr_state:
                
            #     #first case - waiting for department from the first station
            #     case states.WAITING_FOR_FIRST_DEPART:
            #         if((self.start_time[train] < self.time)):
            #             #change status to Loading and calculate potential load:
            #             self.states[train].state = states.LOADING
            #             potential_load=potential_load = min((self.time - self.start_time[train]) / self.gen.beta[0],self.gen.lmax - self.load[train])
            #         if potential_load < self.platform[0]:
            #             self.load[train] = potential_load
            #             self.platform[0] = self.platform[0] - potential_load
            #         else:
            #             self.load = self.platform[0]
            #             self.states[train].state = states.MOVING
            #             self.location[train] = (epoch - (self.platform[0] * self.gen.beta[0])) * self.gen.speed_kmh / 3600
            #             self.platform[0] = 0
                            
            #     case states.LOADING:
            #         potential_load = min(epoch / self.gen.beta[curr_station], self.gen.lmax - self.load[train])
            #         self.loadFunc(train,curr_station,potential_load,0)
                    
            #     case states.UNLOADING:
            #         potential_unload = epoch / self.gen.alpha[curr_station]
            #         if self.load[train] - potential_unload > self.load_before_alight[train] * (1 - self.gen.eta[train, s]):
            #             self.load[train] = self.load[train] - potential_unload
            #         else:
            #             #It will take longer time than epoc to alight all potential alighting passengers:
            #             # 1. unload passengers and calculate unloading time:
            #             self.load[train] = self.load_before_alight[train] * (1 - self.gen.eta[train, s])
            #             unloading_time = (self.load[train] - (self.load_before_alight[train] * (1 - self.gen.eta[train, s]))) * self.gen.alpha[s]
            #             #2. in the meantime start loading passengers, TODO: ask Erez, I think it might be causing a difference
            #             self.states[train].state = states.LOADING
            #             loading_time=(epoch - unloading_time)
            #             potential_load = min((loading_time/ self.gen.beta[s]), self.gen.lmax - self.load[train]) #calculated correctly in my opinion
            #             self.loadFunc(train,curr_station,potential_load,unloading_time)
            #             #state might be changed to moving, it is handled in loadFunc with unloading_time as shift 
                    

                    
            # curr_station=self.states[train].station 
             
                    
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
                self.loadFunc(train,s,potential_load,0)
            # CASE 3 - unloading
            elif self.states[train].state == states.UNLOADING:
                self.load_before_alight[train] = self.load[train] #TODO: check "todo" in MOVING section.
                #It is important to update this field if we have been state-crossing to unloading in the same epoc
                s = self.states[train].station
                potential_unload = epoch / self.gen.alpha[s]
                if self.load[train] - potential_unload > self.load_before_alight[train] * (1 - self.gen.eta[train, s]):
                    self.load[train] = self.load[train] - potential_unload
                else:
                    #It will take longer time than epoc to alight all potential alighting passengers so:
                    # 1. unload passengers and calculate unloading time:
                    self.load[train] = self.load_before_alight[train] * (1 - self.gen.eta[train, s])
                    unloading_time = (self.load[train] - (self.load_before_alight[train] * (1 - self.gen.eta[train, s]))) * self.gen.alpha[s]
                    #2. in the meantime change train state to loading! TODO: ask Erez, I think it might be causing a difference
                    self.states[train].state = states.LOADING
                    loading_time=(epoch - unloading_time)
                    potential_load = min((loading_time/ self.gen.beta[s]), self.gen.lmax - self.load[train]) #calculated correctly in my opinion
                    self.loadFunc(train,s,potential_load,unloading_time)
                    
                    
            # CASE 4 - MOVING
            elif self.states[train].state == states.MOVING:
                potential_move = epoch * self.gen.speed_kmh / 3600
                if potential_move < (10 - (self.location[train]) % 10):
                    #the movement in one epoch is less than the distance to the next station:
                    self.location[train] = self.location[train] + potential_move
                    #we can update the train location on route to the next station and train's status must not be changed!
                else:
                    #the movement in one epoch is greater than the distance to the next station:
                    moving_time = ((10 - (self.location[train]) % 10) / self.gen.speed_kmh) * 3600 #time requried to get to the next station
                    self.location[train] = self.location[train] + 10 - (self.location[train]) % 10  #updates train ocation to where the next station is, removes "tail"
                    self.states[train].station = self.states[train].station + 1 
                    #It is important to notice that as a result, we have some spare time in this epoc so train status can be changed to unloading and passengers shall alight!
                    self.states[train].state = states.UNLOADING
                    self.load_before_alight[train] = self.load[train] #TODO: I think it must be at the end too because we later move to unloading state - COVERED ALREADY INSIDE UNLOADING!
                    s = self.states[train].station #must be assigned again because current_state has been changed!
                    potential_unload = (epoch - moving_time) / self.gen.alpha[s]
                    
                    if potential_unload < self.load_before_alight[train] * self.gen.eta[train, s]:
                        #if the number of alighting passengers is less than what is expected:
                        #only need to update the train load, train stays at UNLOADING state:
                        self.load[train] = self.load[train] - potential_unload
                        #TODO: in the next step the train is at UNLOADING state but load_before_alight is not updated! I think it should be added here:
                        #self.load_before_alight[train] = self.load[train] -IGNORE
                        #TODO: I have better idea - put it in UNLOADING section just before calculating the if statement and then we are covered. 
                        #check other variables that have to follow the same logic
                    else:
                        #the number of alighting passengers is greater than what is expected:
                        #1.substructs the expected number of alighting passengers from the current load on the train and calculates time of alighting:
                        unloading_time = (self.load_before_alight[train] * self.gen.eta[train, s]) * self.gen.alpha[s]
                        self.load[train] = self.load_before_alight[train] * (1 - self.gen.eta[train, s])
                        
                        #2.TODO: ask Erez: why did you change it to loading without a condition? don't we need to check that we have some spare time after unloading?
                        # I'm adding this condition, we assume that the epoch is not big enough that in one step we might be experiencing more than 3 transitions...
                        #moreover, if we don't have transition to loading in this epoch, eventually we will move to loading from unloading state so we won't get stuck.
                        if((epoch - unloading_time)>0):
                        #3 There is a transition in this epoc to LOADING STATE, note that timing window is smaller!
                            self.states[train].state = states.LOADING #change current state to loading
                            potential_load = min((epoch - unloading_time - moving_time) / self.gen.beta[s],self.gen.lmax - self.load[train])
                            timing_shift=unloading_time - moving_time
                            self.loadFunc(train,s,potential_load,timing_shift)


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
file1 = open("new_output.txt","w")
for i in range(1):
    x = 0
    for t in range(600000):
        epoch = 100
        train = 1
        a = sys.states[train].state
        st = "WAITING FOR FIRST DEPART" if a == 0 else (
            "UNLOADING" if a == 1 else (
                "LOADING" if a == 2 else ("MOVING" if a == 3 else ("FINISHED" if a == 4 else "ERROR"))))
        if (st == "MOVING" and x == sys.states[train].station) or True:
            print(t, ": time: ", sys.time, ", location: ", int(sys.location[train]), ", load: ", int(sys.load[train]),f", platform{sys.states[train].station}: ",
                  int(sys.platform[sys.states[train].station]), ", state: ", st, ", station: ",
                  sys.states[train].station,file=file1)
            x = x + 1
        if st != "FINISHED":
            sys.advance(epoch , noise)
        else:
            print("DONE")
            break;
    sys.reset()
    noise = True
file1.close()
