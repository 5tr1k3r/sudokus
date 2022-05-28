import time
from collections import Counter

import config as cfg
from models.puzzle import Puzzle, IndexSet, NumSet, convert_index


def check_if_solved(func):
    def wrapper(self: BaseTechnique):
        if self.puzzle.check_if_solved():
            if cfg.solve_output_enabled:
                print('Puzzle is solved already')

            return False

        if cfg.solve_output_enabled:
            print(f'Applying {self.__class__.__name__} technique')

        time_start = time.perf_counter()
        is_used = func(self)

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

    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def apply(self):
        pass

    def get_candidates_counter(self, group: IndexSet) -> Counter:
        return Counter(cand_value for x, y in group for cand_value in self.puzzle.candidates[y][x])

    def get_candidates_indices_by_value(self, value: int, group: IndexSet) -> IndexSet:
        return {(x, y) for x, y in group if value in self.puzzle.candidates[y][x]}

    def get_candidates_indices_by_exact_candidates(self, cands: NumSet, group: IndexSet) -> IndexSet:
        return {(x, y) for x, y in group if cands == self.puzzle.candidates[y][x]}

    def remove_candidate_from_group(self, candidate_value: int, group: IndexSet) -> bool:
        cells = []
        for x, y in group:
            if candidate_value in self.puzzle.candidates[y][x]:
                self.puzzle.candidates[y][x].discard(candidate_value)
                cells.append((x, y))

        if len(cells) > 0:
            if cfg.solve_output_enabled:
                print(f"  removed candidate {candidate_value} from {', '.join(convert_index(x, y) for x, y in cells)}")
            return True

        return False
