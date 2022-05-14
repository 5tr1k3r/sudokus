from models.puzzle import Puzzle


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
        self.puzzle.remove_candidate_from_rcb(value, x, y)
        self.puzzle.candidates[y][x] = set()
