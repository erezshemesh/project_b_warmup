from train_system import *
from agent import *
'''
TODO : 
I noticed some problems:

1. when optimizing boarding amount , first trains tends to depart late
2. sometimes, when the train capacity is to big and there are alot of people on the platform 
   and on the train it takes a lot of time for this train to depart, this causes a violation
   in the constraint: T << closing_time .
   solution: set a tmax time limit for a train to stay in a station before leaving.
'''

np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})

g = Generator(
    trains=5,
    stations=4,
    t_alight_per_person=3,
    t_board_per_person=4,
    platform_arrivals_per_t=0.1,
    alight_fraction=0.4,
    number_of_carts=10,
    km_between_stations=30,
    speed_kmh=100,
    stop_t=0,
    tmin=180,
    train_capacity=10000,
    platform_capacity=100000,
    var=0
)
constraints = g.make_all_constraints
g.sol = minimize(g.objective_max_board, g.V, method='SLSQP', constraints=constraints, callback=g.callback,
                 options={'maxiter': max_iterations})
Tsol, Lsol, Psol = g.extract(g.sol.x)
print("\nopen times: from ", to_time(g.open_time[0]), " to", to_time(g.close_time[g.stations - 1]))
print("total arrivals: ", int(sum(g.total_arrivals())))
print("total boarded: ",int(sum(g.total_arrivals()) - sum(g.total_to_late_arrivals(Tsol)) - g.objective_min_blocked(g.sol.x)))
print("total blocked: ", int(g.objective_min_blocked(g.sol.x)))
print("total arrived to late: ", int(sum(g.total_to_late_arrivals(Tsol))))

print_result(g)
g.assert_results(g.sol.x, min_error=0.2)
Tsol, Lsol, Psol = g.extract(g.sol.x)

sys = TrainSystem(Tsol, Lsol, Psol, g)
agent=DummyAgent(sys.gen.trains)

noise = False
for i in range(1):
    x = 0
    for t in range(600000):
        epoch = 200
        train = 1
        a = sys.states[train].state
        print("step reward:",sys.step_reward)
        sys.agent_speed=agent.update_speed_vector(sys.states)
        st = "WAITING FOR FIRST DEPART" if a == 0 else (
            "UNLOADING" if a == 1 else (
                "LOADING" if a == 2 else ("MOVING" if a == 3 else ("FINISHED" if a == 4 else "ERROR"))))
        if st == "MOVING" and x == sys.states[train].station or True:
            print(t, ": time: ", sys.time, ", location: ", int(sys.location[train]), ", load: ", int(sys.load[train]),
                  f", platform{sys.states[train].station}: ",
                  int(sys.platform[sys.states[train].station]), ", state: ", st, ", station: ",
                  sys.states[train].station)
            x = x + 1
        if st != "FINISHED":
            sys.step(epoch, noise)
        else:
            print("DONE")
            break
    sys.reset()
    noise = True
