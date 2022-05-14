from collections import Counter

from models.puzzle import Puzzle, IndexSet


def check_if_solved(func):
    def wrapper(self):
        if self.puzzle.is_solved():
            print('Puzzle is solved already')
            return True

        print(f'Applying {self.__class__.__name__} technique')
        return func(self)

    return wrapper


class BaseTechnique:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def apply(self):
        pass

    def assign_value_to_cell(self, value: int, x: int, y: int):
        print(f'  found {value} at position {x, y}')
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

    def remove_candidate_from_group(self, candidate_value: int, group: IndexSet) -> int:
        count = 0
        for x, y in group:
            if candidate_value in self.puzzle.candidates[y][x]:
                self.puzzle.candidates[y][x].discard(candidate_value)
                count += 1

        return count
