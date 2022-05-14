from models.puzzle import Puzzle
from models.tech.hidden_single import HiddenSingle
from models.tech.locked_candidates import LockedCandidates
from models.tech.single_candidate import SingleCandidate


class SudokuSolver:
    def __init__(self):
        self.puzzle = Puzzle.from_file('sudoku2.txt')
        self.tech = [
            SingleCandidate(self.puzzle),
            HiddenSingle(self.puzzle),
            LockedCandidates(self.puzzle),
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

        if self.puzzle.is_solved():
            is_validated = self.puzzle.validate_solution()
            if not is_validated:
                print('Solution is invalid!\n')

        self.display_puzzle()

    def give_breakdown(self):
        current_cell_count = self.puzzle.count_cells()
        total_cells = self.puzzle.size * self.puzzle.size
        print(f'\nOriginal clue count: {self.puzzle.original_clue_count}')
        print(f'Cells solved: {current_cell_count - self.puzzle.original_clue_count}')
        print(f'Final progress: {(current_cell_count / total_cells):.0%}\n')

    def display_puzzle(self):
        for row in self.puzzle.grid:
            print(row)


if __name__ == '__main__':
    solver = SudokuSolver()
    solver.solve()
