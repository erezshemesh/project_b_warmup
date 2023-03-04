from pyRDDLGym import RDDLEnv
from pyRDDLGym import ExampleManager
from pyRDDLGym.Policies.Agents import NoOpAgent
import numpy as np
import random
from scipy.optimize import minimize

np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})


class Generator:

    def __init__(self, trains, stations):
        self.trains = trains
        self.stations = stations
        self.shape = (trains, stations)
        self.alpha = np.random.rand(stations) * 8
        self.beta = np.random.rand(stations) * 5
        self.lambda_ = np.random.rand(stations) * 0.1
        self.eta = np.full(self.shape, 0.7)
        self.R = np.zeros((trains, stations - 1))
        for i in range(trains):
            time = random.randint(100, 110)
            self.R[i] = np.full(stations - 1, time)
        self.S = np.zeros(self.shape)
        for i in range(trains):
            time = random.randint(5, 15)
            self.S[i] = np.full(stations, time)
        self.tmin = 100
        self.lmax = 40000000
        self.pmax = 40000000
        self.T = np.random.rand(trains, stations) * 100
        self.L = np.random.rand(trains, stations) * 100
        self.V = np.concatenate(
            (
                self.T.reshape(self.T.size),
                self.L.reshape(self.L.size)
            )
        )

        def extract(self, V, name='all'):
            assert (V is not None and (name == 'T' or name == 'L' or name == 'all'))
            if name == 'all':
                return self.extract(V, 'T'), self.extract(V, 'L')
            size = int(self.trains * self.stations)
            (start, end) = (0, size) if name == 'T' else (size, 2 * size)
            return V[start:end].reshape(self.trains, self.stations)


class RailWay:
    def __init__(self, stations):
        self.stations = stations
        self.platform_load =