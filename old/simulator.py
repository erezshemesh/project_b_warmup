import numpy as np
import pygame
from pygame.locals import *
from generator import *
import project_b_tools

pygame.init()

RED = (255, 0, 0)
GRAY = (125, 125, 125)


class Objects:
    def __init__(self, g):
        self.g = g
        self.screen = pygame.display.set_mode([(g.stations + 1) * (20 + 100), 800])
        self.stations = [Rect(120 * (j + 1), 0, 20, 20) for j in range(g.stations)]
        self.trains = [Rect(0, 200 + 25 * i, 20, 20) for i in range(g.trains)]
        self.trains_current_station = [-1] * g.trains
        self.stations_current_train = [-1] * g.stations


    def shift(self, i, dx):
        self.trains[i] = self.trains[i].move(dx, 0)


class Simulator:
    def __init__(self, g : Generator):
        self.g = g
        self.T = g.extract(g.sol.x, 'T')
        self.L = g.extract(g.sol.x, 'L')
        self.P = g.extract(g.sol.x, 'P')
        self.objects = Objects(g)

    def relocate_train(self, i, t):
        current_station = self.objects.trains_current_station[i]
        if current_station == self.g.stations - 1:
            return
        t_arrive_to_next_station = self.g.t_arrive_to_station(self.T, i, current_station + 1)
        if t >= t_arrive_to_next_station:
            self.objects.trains_current_station[i] = current_station + 1
            location = 120 * (current_station + 2)
        else:
            t_depart_current_station = self.T[i, current_station]
            location = self.objects.trains[i].left
            if t_depart_current_station <= t < t_arrive_to_next_station:
                t_run = t - t_depart_current_station
                location = 120 * (current_station + 1) + 120 * t_run / self.g.R[i, current_station]
            if t_arrive_to_next_station <= t:
                self.objects.trains_current_station[i] = current_station + 1
                location = 120 * (current_station + 2)
        self.objects.trains[i] = Rect(location, 200 + 25 * i, 20, 20)

    def change_station_residency(self, j, t):
        #current train is the train the is being boarded or the last one that was boraded
        current_train = self.objects.stations_current_train[j]
        if current_train == self.g.trains - 1:
            return
        start_arriving_time = self.g.open_time[j] if current_train == -1 else self.T[current_train, j]
        residency = self.objects.stations[j].height - 20
        if t <= start_arriving_time:
            return
        if start_arriving_time <= t <= self.T[current_train + 1, j]:
            residency = self.g.lambda_[j] * (t - start_arriving_time)
            start_boarding_time = self.g.t_arrive_to_station(self.T, current_train, j) + self.g.t_alight(self.L, current_train, j)
            if t >= start_boarding_time:
                print(f"time = {t}")
                print()
                print(self.g.board_amount(self.L, self.P, current_train, j), (t - start_boarding_time), self.g.t_board(self.L, self.P, current_train, j), self.g.beta[j])
                print(self.g.board_amount(self.L, self.P, current_train, j) * (t - start_boarding_time) / self.g.t_board(self.L, self.P, current_train, j))



                residency = residency - self.g.board_amount(self.L, self.P, current_train, j) * (t - start_boarding_time) / self.g.t_board(self.L, self.P, current_train, j)
        elif t >= self.T[current_train + 1, j]:
            self.objects.stations_current_train[j] = current_train + 1
        size = self.residency_to_station_size(residency)
        self.objects.stations[j] = Rect(120 * (j + 1), 0, size, size)

    def residency_to_station_size(self, res):
        return min(20 + 30 * (res / 10000), 50)






    def texts(self, x):
        text = pygame.font.Font('freesansbold.ttf', 16).render(x, True, (0, 0, 0), (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (60, 20)
        s.objects.screen.blit(text, textRect)
        pygame.display.update()



g = Generator(6,4)
constraints = g.make_all_constraints
g.sol = minimize(g.objective_max_board, g.V, method='SLSQP', constraints=constraints, callback=g.callback,
                 options={'maxiter': max_iterations})

s = Simulator(g)
T = pygame.time.get_ticks()
running = True
Tsol, Lsol, Psol = g.extract(g.sol.x)
print("\nopen times: from ", to_time(g.open_time[0]), " to", to_time(g.close_time[g.stations - 1]))
print("total arrivals: ", int(sum(g.total_arrivals())))
print("total boarded: ",
      int(sum(g.total_arrivals()) - sum(g.total_to_late_arrivals(Tsol)) - g.objective_min_blocked(g.sol.x)))
print("total blocked: ", int(g.objective_min_blocked(g.sol.x)))
print("total arrived to late: ", int(sum(g.total_to_late_arrivals(Tsol))))

print_result(g)

while running:
    t = int((pygame.time.get_ticks() + to_sec('05:30:00') - T))
    s.texts(to_time(t))
    s.objects.screen.fill((255, 255, 255))
    for j in range(s.g.stations):
        #s.change_station_residency(j, t)
        pygame.draw.rect(s.objects.screen, GRAY, s.objects.stations[j])
    for i in range(s.g.trains):
        s.relocate_train(i, t)
        pygame.draw.rect(s.objects.screen, RED, s.objects.trains[i])
    pygame.display.flip()
pygame.quit()
