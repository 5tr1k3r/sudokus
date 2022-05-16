import time
from typing import List, TypeVar

import config as cfg
from models.puzzle import Puzzle
from models.tech.base_tech import BaseTechnique
from models.tech.hidden_single import HiddenSingle
from models.tech.locked_candidates import LockedCandidatesOnLine
from models.tech.locked_candidates_in_box import LockedCandidatesInBox
from models.tech.naked_subset import NakedSubset
from models.tech.single_candidate import SingleCandidate

Technique = TypeVar('Technique', bound=BaseTechnique)


class SudokuSolver:
    batches_path = cfg.root / 'puzzles/batches'

    def __init__(self):
        self.tech = (
            SingleCandidate,
            HiddenSingle,
            LockedCandidatesOnLine,
            LockedCandidatesInBox,
            NakedSubset,
        )
        self.high_priority_tech = (
            SingleCandidate,
            HiddenSingle,
        )

    def solve(self, puzzle: Puzzle) -> bool:
        high_priority_tech = [tech(puzzle) for tech in self.tech if tech in self.high_priority_tech]
        low_priority_tech = [tech(puzzle) for tech in self.tech if tech not in self.high_priority_tech]
        is_validated = False

        while not puzzle.check_if_solved():
            any_progress = False

            self.apply_tech_group(high_priority_tech)
            if puzzle.check_if_solved():
                break

            lp_progress = self.apply_tech_group_once(low_priority_tech)
            any_progress = any_progress or lp_progress
            if not any_progress:
                self.notify_no_progress()
                break

        self.give_breakdown(puzzle)

        if puzzle.check_if_solved():
            is_validated = puzzle.validate_solution()
            if not is_validated:
                self.notify_solution_invalid()

        self.display_puzzle(puzzle)

        return is_validated

    @staticmethod
    def apply_tech_group(group: List[Technique]) -> bool:
        total_progress = False
        while True:
            iteration_progress = False

            for tech in group:
                tech_progress = tech.apply()
                iteration_progress = iteration_progress or tech_progress

            total_progress = total_progress or iteration_progress

            if not iteration_progress:
                return total_progress

    @staticmethod
    def apply_tech_group_once(group: List[Technique]) -> bool:
        total_progress = False

        for tech in group:
            tech_progress = tech.apply()
            total_progress = total_progress or tech_progress

        return total_progress

    def batch_solve(self, filename: str,
                    save_results: bool = False,
                    results_filename: str = None,
                    save_unsolved: bool = False):
        if results_filename is None:
            results_filename = 'results.txt'

        with open(self.batches_path / filename) as f:
            all_puzzles = f.read().splitlines()

        cfg.solve_output_enabled = False
        total_count = len(all_puzzles)
        unsolved = []
        time_start = time.perf_counter()

        for puzzle_string in all_puzzles:
            puzzle = Puzzle.from_string(puzzle_string)
            if not self.solve(puzzle):
                puzzle_state = puzzle.get_puzzle_string()
                unsolved.append(puzzle_state)

        time_taken = time.perf_counter() - time_start

        output = [f'{filename}']
        unsolved_rate = len(unsolved) / total_count
        if save_unsolved:
            with open(self.batches_path / f'unsolved_{filename}', 'w') as f:
                f.write('\n'.join(unsolved))

        time_per_sudoku = time_taken / total_count

        output.append(f'Total: {total_count}, unsolved: {len(unsolved)} ({unsolved_rate:.1%}), '
                      f'took {time_taken:.2f}s ({time_per_sudoku:.4f}s per)')
        for tech in self.tech:
            if tech.total_uses > 0:
                avg_time_per_tech_use = tech.total_time / tech.total_uses
                avg_line = f' ({avg_time_per_tech_use:.6f}s per)'
            else:
                avg_line = ''
            output.append(f'{tech.__name__}: {tech.successful_uses} uses, '
                          f'took {tech.total_time:.2f}s{avg_line}')
            tech.total_uses = 0
            tech.successful_uses = 0
            tech.total_time = 0.0

        output_string = '\n'.join(output) + '\n\n'

        print(output_string)
        if save_results:
            with open(self.batches_path / results_filename, 'a') as f:
                f.write(output_string)

    def batch_solve_everything(self, results_filename: str, save_unsolved=False):
        results_file = self.batches_path / results_filename
        if results_file.is_file():
            print(f'{results_filename} already exists')
            return

        files = ('0.txt', '1.txt', '2.txt', '3.txt', '5.txt')
        for file in files:
            self.batch_solve(file, save_results=True, results_filename=results_filename,
                             save_unsolved=save_unsolved)

    @staticmethod
    def notify_no_progress():
        if cfg.solve_output_enabled:
            print('No progress detected, stopping the solve')

    @staticmethod
    def notify_solution_invalid():
        print('Solution is invalid!\n')

    @staticmethod
    def give_breakdown(puzzle: Puzzle):
        if cfg.solve_output_enabled:
            current_cell_count = puzzle.count_cells()
            total_cells = puzzle.size * puzzle.size
            print(f'\nOriginal clue count: {puzzle.original_clue_count}')
            print(f'Cells solved: {current_cell_count - puzzle.original_clue_count}')
            print(f'Final progress: {(current_cell_count / total_cells):.0%}\n')

    @staticmethod
    def display_puzzle(puzzle: Puzzle):
        if cfg.solve_output_enabled:
            for row in puzzle.grid:
                print(row)


if __name__ == '__main__':
    solver = SudokuSolver()
    # p = Puzzle.from_file('sudoku.txt')
    # p = Puzzle.from_string('708000309309180200000700008270600001000200803800010000005006000100307650037000002')
    # solver.solve(p)

    # solver.batch_solve_everything('results.txt')
    solver.batch_solve('ez1k.txt')
