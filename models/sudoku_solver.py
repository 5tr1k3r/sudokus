from models.puzzle import Puzzle
# from models.tech.hidden_single import HiddenSingle
from models.tech.single_candidate import SingleCandidate


class SudokuSolver:
    def __init__(self):
        self.puzzle = Puzzle('sudoku2.txt')
        self.tech = [
            SingleCandidate(self.puzzle),
            # HiddenSingle(self.puzzle),
        ]

    def solve(self):
        while not self.puzzle.is_solved():
            any_progress = False

            for tech in self.tech:
                success = tech.apply()
                any_progress = any_progress or success

            if not any_progress:
                print('No progress anymore, stopping the program')
                break

        self.puzzle.prettyprint_grid()


if __name__ == '__main__':
    solver = SudokuSolver()
    solver.solve()
