from collections import Counter
from string import ascii_uppercase

import config as cfg
from models.puzzle import Puzzle, IndexSet, NumSet


def check_if_solved(func):
    def wrapper(self):
        if self.puzzle.check_if_solved():
            if cfg.solve_output_enabled:
                print('Puzzle is solved already')

            return False

        if cfg.solve_output_enabled:
            print(f'Applying {self.__class__.__name__} technique')

        is_used = func(self)
        if is_used:
            self.__class__.uses += 1

        return is_used

    return wrapper


def convert_index(x: int, y: int) -> str:
    return ascii_uppercase[y] + str(x + 1)


class BaseTechnique:
    uses = 0

    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def apply(self):
        pass

    def assign_value_to_cell(self, value: int, x: int, y: int):
        if cfg.solve_output_enabled:
            print(f'  found {value} at position {convert_index(x, y)}')

        self.puzzle.grid[y][x] = value
        self.remove_candidate_from_rcb(value, x, y)
        self.puzzle.candidates[y][x] = set()

    def remove_candidate_from_rcb(self, candidate: int, x: int, y: int):
        for i, j in self.puzzle.get_rcb_indices(x, y):
            self.puzzle.candidates[j][i].discard(candidate)

    def get_candidates_counter(self, group: IndexSet) -> Counter:
        counter = Counter()
        for x, y in group:
            counter.update(self.puzzle.candidates[y][x])

        return counter

    def get_candidates_indices_by_value(self, value: int, group: IndexSet) -> IndexSet:
        return {(x, y) for x, y in group if value in self.puzzle.candidates[y][x]}

    def get_candidates_indices_by_exact_candidates(self, cands: NumSet, group: IndexSet) -> IndexSet:
        return {(x, y) for x, y in group if cands == self.puzzle.candidates[y][x]}

    def remove_candidate_from_group(self, candidate_value: int, group: IndexSet) -> int:
        cells = []
        for x, y in group:
            if candidate_value in self.puzzle.candidates[y][x]:
                self.puzzle.candidates[y][x].discard(candidate_value)
                cells.append((x, y))

        if (cell_count := len(cells)) > 0 and cfg.solve_output_enabled:
            print(f"  removed candidate {candidate_value} from {', '.join(convert_index(x, y) for x, y in cells)}")

        return cell_count
