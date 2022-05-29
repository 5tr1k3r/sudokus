import time

import config as cfg
from models.puzzle import Puzzle


def check_if_solved_and_update_stats(func):
    def wrapper(self: BaseTechnique, puzzle: Puzzle):
        if puzzle.check_if_solved():
            if cfg.solve_output_enabled:
                print('Puzzle is solved already')

            return False

        if cfg.solve_output_enabled:
            print(f'Applying {self.__class__.__name__} technique')

        time_start = time.perf_counter()
        is_used = func(self, puzzle)

        self.__class__.total_time += time.perf_counter() - time_start
        self.__class__.total_uses += 1
        if is_used:
            self.__class__.successful_uses += 1

        return is_used

    return wrapper


class BaseTechnique:
    total_uses = 0
    successful_uses = 0
    total_time = 0.0

    def apply(self, puzzle: Puzzle):
        pass
