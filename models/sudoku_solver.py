from models.puzzle import Puzzle
from models.tech.hidden_single import HiddenSingle
from models.tech.locked_candidates import LockedCandidates
from models.tech.single_candidate import SingleCandidate


class SudokuSolver:
    def __init__(self):
        self.tech = [
            SingleCandidate,
            HiddenSingle,
            LockedCandidates,
        ]

    def solve(self, puzzle: Puzzle) -> bool:
        tech_instances = [tech(puzzle) for tech in self.tech]
        is_validated = False

        while not puzzle.is_solved():
            any_progress = False

            for tech in tech_instances:
                success = tech.apply()
                any_progress = any_progress or success

            if not any_progress:
                print('No progress detected, stopping the solve')
                break

        self.give_breakdown(puzzle)

        if puzzle.is_solved():
            is_validated = puzzle.validate_solution()
            if not is_validated:
                print('Solution is invalid!\n')

        self.display_puzzle(puzzle)

        return is_validated

    @staticmethod
    def give_breakdown(puzzle: Puzzle):
        current_cell_count = puzzle.count_cells()
        total_cells = puzzle.size * puzzle.size
        print(f'\nOriginal clue count: {puzzle.original_clue_count}')
        print(f'Cells solved: {current_cell_count - puzzle.original_clue_count}')
        print(f'Final progress: {(current_cell_count / total_cells):.0%}\n')

    @staticmethod
    def display_puzzle(puzzle: Puzzle):
        for row in puzzle.grid:
            print(row)


if __name__ == '__main__':
    solver = SudokuSolver()
    p = Puzzle.from_file('sudoku.txt')
    solver.solve(p)
