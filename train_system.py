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
        self.step_reward = 0

    def reset(self):
        self.time = 21600  # 6:00AM
        self.location = np.zeros(self.gen.trains)
        self.states = []
        for _ in range(self.gen.trains):
            self.states += [TrainState()]
        self.load = np.zeros(self.gen.trains)
        self.load_before_alight = np.zeros(self.gen.trains)
        self.platform = np.zeros(self.gen.stations)
        self.agent_speed = np.zeros(self.gen.trains)

    def Wait(self, train, epoch):
        max_wait = self.start_time[train] - self.time
        if epoch > max_wait:
            self.Load(train, epoch - max_wait)

    def Load(self, train, effective_epoch):
        self.states[train].state = states.LOADING
        if effective_epoch > 0:
            station = self.states[train].station
            potential_load = min(effective_epoch / self.gen.beta[station], self.gen.lmax - self.load[train])
            self.load[train] += min(potential_load, self.platform[station])
            if potential_load < self.platform[station]:
                self.platform[station] -= potential_load
                if self.load[train] == self.gen.lmax:
                    loading_time = (potential_load * self.gen.beta[station])
                    self.Move(train, effective_epoch - loading_time)
            else:
                loading_time = (self.platform[station] * self.gen.beta[station])
                self.platform[station] = 0
                self.Move(train, effective_epoch - loading_time)

    def Unload(self, train, effective_epoch):
        self.states[train].state = states.UNLOADING  # maybe it should be outside, think about it later
        if effective_epoch > 0:
            station = self.states[train].station
            potential_unload = effective_epoch / self.gen.alpha[station]
            max_unload = self.load[train] - self.load_before_alight[train] * (1 - self.gen.eta[train, station])
            self.load[train] -= min(potential_unload, max_unload)
            if potential_unload >= max_unload:
                self.Load(train, effective_epoch - max_unload * self.gen.alpha[station])

    def Move(self, train, effective_epoch):
        self.states[train].state = states.MOVING
        self.speed_rewarding(train,effective_epoch)
        speed = (self.gen.speed_kmh / units.hour) + self.agent_speed[train]
        if(self.states[train].station==self.gen.stations-1):
            self.states[train].state = states.FINISHED
        else:
            if effective_epoch > 0:
                potential_move = effective_epoch * speed
                max_move = (10 - (self.location[train]) % 10)
                moving_distance = min(potential_move, max_move)
                moving_time = moving_distance / speed
                self.location[train] += moving_distance
                if potential_move >= max_move:
                    self.states[train].station += 1
                    self.load_before_alight[train] = self.load[train]
                    self.Unload(train, effective_epoch - moving_time)

    def step(self, epoch=60, noise=0):
        self.time = self.time + epoch
        for i in range(self.gen.stations):
            if self.gen.open_time[i] <= self.time <= self.gen.close_time[i]:
                self.platform[i] = self.platform[i] + (self.gen.lambda_[i] + noise * random.uniform(-0.3, 1.2)) * epoch
        for train in range(self.gen.trains):
            # CASE 0 - Finished
            if self.states[train].state == states.MOVING and self.states[train].station == self.gen.stations - 1:
                self.states[train].state = states.FINISHED
                print("Train")
            elif self.states[train].state == states.WAITING_FOR_FIRST_DEPART:
                self.Wait(train, epoch)
            # CASE 2 - loading
            elif self.states[train].state == states.LOADING:
                self.Load(train, epoch)
            # CASE 3 - Unloading
            elif self.states[train].state == states.UNLOADING:
                self.Unload(train, epoch)
            # CASE 4 - Moving
            elif self.states[train].state == states.MOVING:
                self.Move(train, epoch)

    def state(self):
        return np.concatenate(self.load, self.location, self.platform, np.array(self.time), axis=0)
    
    
    def speed_policy_reward_1(self,train,eff_move_time):
        if(train<self.gen.trains-1):
            #current train variables:
            curr_train_loc=self.location[train]
            curr_train_speed=(self.gen.speed_kmh / units.hour) + self.agent_speed[train]
            curr_train_station = self.states[train].station
            #next train variables:
            next_train_loc=self.location[train+1]
            next_train_speed=(self.gen.speed_kmh / units.hour) + self.agent_speed[train+1]
            next_train_state = self.states[train+1].state
            next_train_station=self.states[train+1].station
            
            if(next_train_state==states.MOVING and curr_train_station==next_train_station):
                if(curr_train_loc+eff_move_time*curr_train_speed > next_train_loc + eff_move_time*next_train_speed):
                    self.step_reward -= self.gen.trains #TODO: negative reward for example, ask Ayal
                else:
                    self.step_reward += 1 #TODO: positive reward for example, ask Ayal
                    
    def speed_policy_reward_2(self,train,eff_move_time,epoch,stations_distance): 
        #TODO: added 14.3.23 , we might need to save "full epoch" in self.variable to calculate some relative conditions such as that.
        curr_train_speed=(self.gen.speed_kmh / units.hour) + self.agent_speed[train]
        potential_distance=eff_move_time*curr_train_speed
        if(potential_distance > stations_distance * (eff_move_time)/epoch):
            self.step_reward -= self.gen.trains
        else:
            self.step_reward += 1
            
    #def speed_policy_reward_3 (self,train,eff_move_time):
        #I think it might be like reward_2 but with negative speed. Should think about it
        
    
    def speed_rewarding(self,train,eff_move_time):
        #It may be relevant only when current train is MOVING so all these kind of rewardings should be gathered here as for now
        
        #One train can't pass another one while moving:
        self.speed_policy_reward_1(train,eff_move_time) 
        #.... need to think about more cases ... 
        #Can't cover a distance greater than distance of two adjacent stations in one epoch: (relative)
        self
        
        
    def get_step_reward(self):
        #TODO: as far as I concerned,  there is some memory for rewards in PPO
        episode_reward=self.step_reward
        self.step_reward=0 #reset, prepare it for the next episode
        return episode_reward


import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import gym
