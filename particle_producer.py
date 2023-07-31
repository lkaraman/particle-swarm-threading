import threading
import time
import random
import numpy as np

from consts import NUM_DIMENSIONS, NUMBER_OF_PARTICLES, MAX_ITERATIONS

threadLock = threading.Lock()


class ParticleSwarmProducer(threading.Thread):
    """ Synchronizes all particles and computes their next position/velocity"""
    def __init__(self,
                 initial_particle_position,
                 bounds,
                 dict_shared_errors,
                 dict_shared_is_ready,
                 dict_shared_new_position,
                 dict_shared_best_positions,
                 dict_velocity,
                 condition_wait):

        threading.Thread.__init__(self)

        self.initial_particle_positions = initial_particle_position
        self.bounds = bounds

        self.dict_velocity = dict_velocity

        self.dict_best_positions = dict_shared_best_positions
        self.dict_shared_errors = dict_shared_errors
        self.dict_shared_is_ready = dict_shared_is_ready
        self.dict_shared_new_position = dict_shared_new_position

        self.condition_wait = condition_wait

        self.current_iteration = 0
        self.err_best_g = -1  # best error for group
        self.pos_best_g = []  # best position for group

        # Used for plotting
        self.output_pos = {i: np.empty((0, NUM_DIMENSIONS)) for i in range(NUMBER_OF_PARTICLES)}

    def run(self) -> None:

        i = 1
        while i < MAX_ITERATIONS+1:
            threadLock.acquire(blocking=True)
            ready = list(self.dict_shared_is_ready.values())

            # If all particles have finished their current jobs...
            if all(ready):
                print(f'Iteration {i}')
                print(f'Current positions: {self.dict_shared_new_position}')
                print(f'Current errors: {self.dict_shared_errors}')
                print(f'Current velocities: {self.dict_velocity}')

                self.add_pos_to_out()

                self.evaluate_all_particles()
                self.update_all_particles()

                print('All particles go!')

                with self.condition_wait:
                    self.condition_wait.notifyAll()
                i += 1
            threadLock.release()
            # time.sleep(0.2)

            time.sleep(0.02)
        with self.condition_wait:
            self.condition_wait.notifyAll()
        print(f'Current positions: {self.dict_shared_new_position}')
        print(f'Error: {self.err_best_g}')


    def evaluate_all_particles(self):
        for i in range(NUMBER_OF_PARTICLES):
            if self.dict_shared_errors[i] < self.err_best_g or self.err_best_g == -1:
                self.pos_best_g = list(self.dict_shared_new_position[i])
                self.err_best_g = float(self.dict_shared_errors[i])

    def update_all_particles(self):
        for i in range(NUMBER_OF_PARTICLES):
            self.update_velocity(i)
            self.update_position(i)

    def add_pos_to_out(self):
        for i in range(NUMBER_OF_PARTICLES):
            self.output_pos[i] = np.vstack((self.output_pos[i], self.dict_shared_new_position[i]))

    def update_velocity(self, i):
        w = 0.5  # constant inertia weight (how much to weigh the previous velocity)
        c1 = 1  # cognative constant
        c2 = 2  # social constant

        for j in range(0, NUM_DIMENSIONS):
            r1 = random.random()
            r2 = random.random()

            vel_cognitive = c1 * r1 * (self.dict_best_positions[i][j] - self.dict_shared_new_position[i][j])
            vel_social = c2 * r2 * (self.pos_best_g[j] - self.dict_shared_new_position[i][j])

            self.dict_velocity[i][j] = w * self.dict_velocity[i][j] + vel_cognitive + vel_social

    def update_position(self, i):
        for j in range(0, NUM_DIMENSIONS):
            self.dict_shared_new_position[i][j] = self.dict_shared_new_position[i][j] + self.dict_velocity[i][j]

            # adjust maximum position if necessary
            if self.dict_shared_new_position[i][j] > self.bounds[i][1]:
                self.dict_shared_new_position[i][j] = self.bounds[i][1]

            # adjust minimum position if neseccary
            if self.dict_shared_new_position[i][j] < self.bounds[i][0]:
                self.dict_shared_new_position[i][j] = self.bounds[i][0]
