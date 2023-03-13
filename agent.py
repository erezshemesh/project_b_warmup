from train_system import *
from generator import *

class DummyAgent:
    
    def __init__(self,train_num):
        self.speed_vec_size=train_num
        self.agent_speed = np.zeros(train_num)
        self.episode_period = 8 #example
        self.reward_mem = []
        

    # def change_speed_of_train(self,train,speed):
    #     self.speed_vector[train]=self.speed_vector[train]+speed
        
    def update_speed_vector(self,states):
        for i in range(self.speed_vec_size):
            self.agent_speed[i]=0
        return self.agent_speed
