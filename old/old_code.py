from pyRDDLGym import RDDLEnv
from pyRDDLGym import ExampleManager
from pyRDDLGym.Policies.Agents import NoOpAgent
import numpy as np



env = RDDLEnv.RDDLEnv(domain="test.rddl", instance="warmup_instance_0.rddl")

# set up an aget
agent = NoOpAgent(action_space=env.action_space, num_actions=env.NumConcurrentActions)

total_reward = 0
state = env.reset()
for _ in range(env.horizon):
    env.render()
    next_state, reward, done, info = env.step(agent.sample_action())
    total_reward += reward
    state = next_state
    if done:
        break
    print(state)
env.close()
'''
'''
n_trains = 8
n_stations = 9  # including station 0
epoch = 300

alpha = np.random.rand(n_stations)  # ignoring dummy station value
beta = np.random.rand(n_stations)  # ignoring dummy station value

lambda_ = np.random.rand(n_stations)  # ignoring dummy station value

eta = np.random.rand(n_trains, n_stations)  # ignoring dummy station value
R = np.random.rand(n_trains,
                   n_stations - 1) * 100  # NOT ignoring dummy station value , and does not have value for the last station (obviously)

S = np.random.rand(n_trains, n_stations) * 20  # ignoring dummy station value

T = np.zeros((n_trains, n_stations))
L = np.zeros((n_trains, n_stations))


for i in range(2):
    if i == 0:
        T[i, 0] = S[0, 0] / (1 - beta[0] * lambda_[0])
    else:
        T[i, 0] = (S[0, 0] -  beta[0] * lambda_[0] * T[i-1, 0]) / (1 - beta[0] * lambda_[0])

# initializing values for the dummy station
for i in range(n_trains):
    T[i, 0] = epoch * i
    L[i, 0] = 0

# calculating predetermined timetable
for j in range(1, n_stations):
    for i in range(n_trains):
        if i > 0:
            T_eff = T[i - 1, j]
        else:
            T_eff = 0
        a = (T[i, j - 1] + R[i, j - 1] + S[i, j] - beta[j] * lambda_[j] * T_eff + alpha[j] * eta[i, j] * L[i, j])
        b = (1 - beta[j] * lambda_[j])
        T[i, j] = (T[i, j - 1] + R[i, j - 1] + S[i, j] - beta[j] * lambda_[j] * T_eff + alpha[j] * eta[i, j] * L[i, j]) / (1 - beta[j] * lambda_[j])
        L[i, j] = (1 - eta[i, j]) * L[i, j - 1] + lambda_[j] * (T[i, j] - T_eff)
print("Time table")
print(T.astype(int))

print("Load table")
print(L.astype(int))


# reset T[i,0] L[i,0]



# calculating the error using random noise , and NoOpAgent
w = np.random.rand(n_trains, n_stations) * 7
u = np.zeros(n_trains, n_stations)
