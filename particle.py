import threading

from consts import MAX_ITERATIONS

threadLock = threading.Lock()


class Particle(threading.Thread):
    """ Represents one particle object with specific position/velocity"""
    def __init__(self,
                 thread_id,
                 name,
                 dict_shared_errors,
                 dict_shared_is_ready,
                 dict_shared_new_position,
                 dict_shared_best_positions,
                 fnc,
                 condition_wait
                 ):
        threading.Thread.__init__(self)

        self.thread_id = thread_id
        self.name = name

        self.dict_shared_errors = dict_shared_errors
        self.dict_shared_is_ready = dict_shared_is_ready
        self.dict_shared_new_positions = dict_shared_new_position
        self.dict_shared_best_positions = dict_shared_best_positions

        self.fnc = fnc
        self.condition_wait = condition_wait

    def run(self) -> None:

        it = 1
        best_particle_error = 9999

        while it < MAX_ITERATIONS+1:
            # print(f'{self.name} waiting for a new job...')
            threadLock.acquire(blocking=True)
            self.dict_shared_is_ready[self.thread_id] = True
            threadLock.release()

            with self.condition_wait:
                self.condition_wait.wait()

            threadLock.acquire(blocking=True)
            position = self.dict_shared_new_positions[self.thread_id]
            error = self.fnc(position)

            if error < best_particle_error:
                self.dict_shared_best_positions[self.thread_id] = position
                best_particle_error = error

            self.dict_shared_errors[self.thread_id] = self.fnc(position)

            # set to not ready
            self.dict_shared_is_ready[self.thread_id] = False
            threadLock.release()
            # print(f'{self.name} working on task')
            it +=1
            # print(f'{self.name}, {it}')
