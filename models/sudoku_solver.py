import random
import time
from typing import List, TypeVar

import config as cfg
from models.puzzle import Puzzle
from models.tech.base_tech import BaseTechnique
from models.tech.hidden_single import HiddenSingle
from models.tech.hidden_subset import HiddenSubset
from models.tech.locked_candidates import LockedCandidatesOnLine
from models.tech.locked_candidates_in_box import LockedCandidatesInBox
from models.tech.naked_subset import NakedSubset
from models.tech.single_candidate import SingleCandidate
from models.tech.x_wing import XWing

Technique = TypeVar('Technique', bound=BaseTechnique)


class SudokuSolver:
    batches_path = cfg.root / 'puzzles/batches'

    def __init__(self):
        self.tech = (
            SingleCandidate,
            HiddenSingle,
            NakedSubset,
            LockedCandidatesOnLine,
            LockedCandidatesInBox,
            XWing,
            HiddenSubset,
        )
        self.high_priority_tech = (
            SingleCandidate,
            HiddenSingle,
        )
        self.low_priority_tech = (
            LockedCandidatesInBox,
            XWing,
            HiddenSubset,
        )

    def solve(self, puzzle: Puzzle) -> bool:
        high_priority_tech = [tech(puzzle) for tech in self.tech if tech in self.high_priority_tech]
        normal_priority_tech = [tech(puzzle) for tech in self.tech if tech not in self.high_priority_tech
                                and tech not in self.low_priority_tech]
        low_priority_tech = [tech(puzzle) for tech in self.tech if tech in self.low_priority_tech]
        is_validated = False

        while not puzzle.check_if_solved():
            any_progress = False

            self.apply_tech_group(high_priority_tech)
            if puzzle.check_if_solved():
                break

            lp_progress = self.apply_tech_group_once(normal_priority_tech)
            any_progress = any_progress or lp_progress
            if not any_progress:
                if not self.apply_tech_group_once(low_priority_tech):
                    self.notify_no_progress()
                    break

        self.give_breakdown(puzzle)

        if puzzle.check_if_solved():
            is_validated = puzzle.validate_solution()
            if not is_validated:
                self.notify_solution_invalid()
        else:
            self.show_puzzle_string(puzzle)

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
        unsolved = []
        time_start = time.perf_counter()

        for puzzle_string in all_puzzles:
            puzzle = Puzzle.from_string(puzzle_string)
            if not self.solve(puzzle):
                puzzle_state = puzzle.get_puzzle_string()
                unsolved.append(puzzle_state)

        time_taken = time.perf_counter() - time_start

        if save_unsolved:
            with open(self.batches_path / f'unsolved_{filename}', 'w') as f:
                f.write('\n'.join(unsolved))

        output_string = self.construct_result_string(filename, len(all_puzzles),
                                                     len(unsolved), time_taken)
        print(output_string)
        if save_results:
            with open(self.batches_path / results_filename, 'a', encoding='utf-8') as f:
                f.write(output_string)

        self.reset_tech_stats()

    def batch_solve_everything(self, results_filename: str, save_unsolved=False):
        results_file = self.batches_path / results_filename
        if results_file.is_file():
            print(f'{results_filename} already exists')
            return

        files = ('0.txt', '1.txt', '2.txt', '3.txt', '5.txt')
        for file in files:
            self.batch_solve(file, save_results=True, results_filename=results_filename,
                             save_unsolved=save_unsolved)

    def solve_random_from_batch(self, batch_filename: str):
        with open(self.batches_path / batch_filename) as f:
            all_puzzles = f.read().splitlines()

        puzzle_string = random.choice(all_puzzles)
        puzzle = Puzzle.from_string(puzzle_string)
        print(f'Solving {puzzle_string}\n')
        self.solve(puzzle)

    def reset_tech_stats(self):
        for tech in self.tech:
            tech.total_uses = 0
            tech.successful_uses = 0
            tech.total_time = 0.0

    def construct_result_string(self, filename: str, total_count: int,
                                unsolved_count: int, time_taken: float) -> str:
        hp_line = ', '.join(tech.__name__ for tech in self.high_priority_tech)
        output = [f'{filename} | High priority tech: {hp_line}']
        unsolved_rate = unsolved_count / total_count
        time_per_sudoku = time_taken / total_count
        output.append(f'Total: {total_count}, unsolved: {unsolved_count} ({unsolved_rate:.1%}), '
                      f'took {time_taken:.2f}s ({(time_per_sudoku * 1000):.1f}ms per)')
        for tech in self.tech:
            if tech.total_uses > 0:
                avg_time_per_tech_use = tech.total_time / tech.total_uses * 10 ** 6
                avg_line = f' ({round(avg_time_per_tech_use)}μs per)'
            else:
                avg_line = ''
            output.append(f'{tech.__name__}: {tech.successful_uses}/{tech.total_uses} uses, '
                          f'took {tech.total_time:.2f}s{avg_line}')

        total_uses = sum(tech.total_uses for tech in self.tech)
        total_time = sum(tech.total_time for tech in self.tech)
        avg_time = total_time / total_uses * 10 ** 6
        output.append(f'TOTAL USES: {total_uses}, {round(avg_time)}μs per')

        return '\n'.join(output) + '\n\n'

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

    @staticmethod
    def show_puzzle_string(puzzle: Puzzle):
        if cfg.solve_output_enabled:
            print('Final puzzle state:')
            print(puzzle.get_puzzle_string())
            print()


if __name__ == '__main__':
    solver = SudokuSolver()
    # p = Puzzle.from_file('sudoku.txt')
    # p = Puzzle.from_string('708000309309180200000700008270600001000200803800010000005006000100307650037000002')
    # solver.solve(p)

    # solver.batch_solve_everything('results.txt')
    solver.batch_solve('ez1k.txt')
