from models.puzzle import Puzzle
from models.tech.hidden_single import HiddenSingle
from models.tech.single_candidate import SingleCandidate


class SudokuSolver:
    def __init__(self):
        self.puzzle = Puzzle('sudoku2.txt')
        self.tech = [
            SingleCandidate(self.puzzle),
            HiddenSingle(self.puzzle),
        ]

    def solve(self):
        while not self.puzzle.is_solved():
            any_progress = False

            for tech in self.tech:
                success = tech.apply()
                any_progress = any_progress or success

            if not any_progress:
                print('No progress detected, stopping the program')
                break

        self.give_breakdown()
        self.puzzle.prettyprint_grid()

    def give_breakdown(self):
        current_cell_count = self.puzzle.count_cells()
        total_cells = self.puzzle.size * self.puzzle.size
        print(f'\nOriginal clue count: {self.puzzle.original_clue_count}')
        print(f'Cells solved: {current_cell_count - self.puzzle.original_clue_count}')
        print(f'Final progress: {(current_cell_count / total_cells):.0%}\n')


if __name__ == '__main__':
    solver = SudokuSolver()
    solver.solve()
