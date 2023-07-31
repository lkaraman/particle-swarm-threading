import threading
import random

from consts import NUM_DIMENSIONS, NUMBER_OF_PARTICLES
from particle import Particle
from particle_producer import ParticleSwarmProducer

import numpy as np


# Function to optimize
def fnc(x):
    total=0
    for i in range(len(x)):
        total+=x[i]**2
    return total


if __name__ == '__main__':
    x_down, x_up = (-100, 100)

    # All shared datastrucures between particles and particle producer
    dict_shared_new_position = {i: list(np.random.uniform(x_down, x_up, NUM_DIMENSIONS)) for i in range(0, NUMBER_OF_PARTICLES)}
    dict_shared_best_position = dict_shared_new_position.copy()
    dict_velocity = {i: [random.uniform(-1,1)] * NUM_DIMENSIONS for i in range(0, NUMBER_OF_PARTICLES)}
    dict_shared_errors = {i: -1 for i in range(0, NUMBER_OF_PARTICLES)}
    dict_shared_is_ready = {i: False for i in range(0, NUMBER_OF_PARTICLES)}

    bounds = [(x_down, x_up) for i in range(NUMBER_OF_PARTICLES)]

    condition_wait = threading.Condition()


    producer = ParticleSwarmProducer(initial_particle_position=dict_shared_new_position,
                                     bounds=bounds,
                                     dict_shared_errors=dict_shared_errors,
                                     dict_shared_is_ready=dict_shared_is_ready,
                                     dict_shared_new_position=dict_shared_new_position,
                                     dict_shared_best_positions=dict_shared_best_position,
                                     dict_velocity=dict_velocity,
                                     condition_wait=condition_wait
                                     )

    particles = []

    for i in range(NUMBER_OF_PARTICLES):
        p = Particle(thread_id=i,
                     name='Thread ' + str(i+1),
                     dict_shared_errors=dict_shared_errors,
                     dict_shared_is_ready=dict_shared_is_ready,
                     dict_shared_new_position=dict_shared_new_position,
                     dict_shared_best_positions=dict_shared_best_position,
                     fnc=fnc,
                     condition_wait=condition_wait)
        particles.append(p)

    producer.start()

    for p in particles:
        p.start()

    producer.join()

    for p in particles:
        p.join()

