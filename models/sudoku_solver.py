import random
import time
from typing import List, TypeVar

import config as cfg
from models.puzzle import Puzzle, convert_index
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
        self.tech_classes = (
            SingleCandidate,
            HiddenSingle,
            NakedSubset,
            LockedCandidatesOnLine,
            # LockedCandidatesInBox,
            # XWing,
            # HiddenSubset,
        )
        self.hp_tech_classes = (
            SingleCandidate,
            HiddenSingle,
        )
        self.lp_tech_classes = (
            LockedCandidatesInBox,
            XWing,
            HiddenSubset,
        )

        self.high_priority_tech = [tech() for tech in self.tech_classes if tech in self.hp_tech_classes]
        self.normal_priority_tech = [tech() for tech in self.tech_classes if tech not in self.hp_tech_classes
                                     and tech not in self.lp_tech_classes]
        self.low_priority_tech = [tech() for tech in self.tech_classes if tech in self.lp_tech_classes]

        self.bruteforce_counter = 0

    def solve(self, original_puzzle: Puzzle) -> bool:
        queue: List[Puzzle] = [original_puzzle]

        while queue:
            puzzle = queue.pop()
            if self.solve_logically(puzzle):
                if cfg.solve_output_enabled:
                    print("Puzzle solved\n")
                return True

            if puzzle.is_impossible():
                if cfg.solve_output_enabled:
                    print(f'Puzzle is impossible to solve!')
                    # print(puzzle.fancy_display())
                continue

            self.bruteforce_counter += 1

            x, y = puzzle.find_cell_with_fewest_candidates()
            if cfg.solve_output_enabled:
                print(f'Going to pick cell {convert_index(x, y)} and bruteforce from there')

            for cand in puzzle.candidates[y][x]:
                new_puzzle = puzzle.copy()
                new_puzzle.assign_value_to_cell(cand, x, y)
                queue.append(new_puzzle)

        return False

    def solve_logically(self, puzzle: Puzzle) -> bool:
        is_validated = False

        while not puzzle.check_if_solved():
            any_progress = False

            self.apply_tech_group_repeatedly(puzzle, self.high_priority_tech)
            if puzzle.check_if_solved():
                break

            lp_progress = self.apply_tech_group_once(puzzle, self.normal_priority_tech)
            any_progress = any_progress or lp_progress
            if not any_progress:
                if not self.apply_tech_group_once(puzzle, self.low_priority_tech):
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
    def apply_tech_group_repeatedly(puzzle: Puzzle, group: List[Technique]) -> bool:
        total_progress = False
        while True:
            iteration_progress = False

            for tech in group:
                tech_progress = tech.apply(puzzle)
                iteration_progress = iteration_progress or tech_progress

            total_progress = total_progress or iteration_progress

            if not iteration_progress:
                return total_progress

    @staticmethod
    def apply_tech_group_once(puzzle: Puzzle, group: List[Technique]) -> bool:
        total_progress = False

        for tech in group:
            tech_progress = tech.apply(puzzle)
            total_progress = total_progress or tech_progress

        return total_progress

    def batch_solve(self, filename: str,
                    save_results: bool = False,
                    results_filename: str = None,
                    save_unsolved: bool = False) -> float:
        if results_filename is None:
            results_filename = 'results.txt'

        self.bruteforce_counter = 0

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

        return time_taken

    def batch_solve_everything(self, results_filename: str, save_unsolved=False):
        results_file = self.batches_path / results_filename
        if results_file.is_file():
            print(f'{results_filename} already exists')
            return

        files = ('0.txt', '1.txt', '2.txt', '3.txt', '5.txt')
        total_time_taken = 0
        for file in files:
            time_taken = self.batch_solve(file, save_results=True, results_filename=results_filename,
                                          save_unsolved=save_unsolved)
            total_time_taken += time_taken

        with open(self.batches_path / results_filename, 'a', encoding='utf-8') as f:
            total_time_line = f'Total time taken: {total_time_taken:.2f}s'
            print(total_time_line)
            f.write(total_time_line)

    def solve_random_from_batch(self, batch_filename: str):
        with open(self.batches_path / batch_filename) as f:
            all_puzzles = f.read().splitlines()

        puzzle_string = random.choice(all_puzzles)
        puzzle = Puzzle.from_string(puzzle_string)
        print(f'Solving {puzzle_string}\n')
        self.solve(puzzle)

    def reset_tech_stats(self):
        for tech in self.tech_classes:
            tech.total_uses = 0
            tech.successful_uses = 0
            tech.total_time = 0.0

    def construct_result_string(self, filename: str, total_count: int,
                                unsolved_count: int, time_taken: float) -> str:
        hp_line = ', '.join(tech.__name__ for tech in self.hp_tech_classes)
        output = [f'{filename} | High priority tech: {hp_line}']
        unsolved_rate = unsolved_count / total_count
        time_per_sudoku = time_taken / total_count
        output.append(f'Total: {total_count}, unsolved: {unsolved_count} ({unsolved_rate:.1%}), '
                      f'took {time_taken:.2f}s ({(time_per_sudoku * 1000):.1f}ms per)')
        for tech in self.tech_classes:
            if tech.total_uses > 0:
                avg_time_per_tech_use = tech.total_time / tech.total_uses * 10 ** 6
                avg_line = f' ({round(avg_time_per_tech_use)}??s per)'
            else:
                avg_line = ''

            use_rate = tech.successful_uses / tech.total_uses
            output.append(f'{tech.__name__}: {tech.successful_uses}/{tech.total_uses} uses ({use_rate:.0%}), '
                          f'took {tech.total_time:.2f}s{avg_line}')

        output.append(f'Used bruteforce {self.bruteforce_counter} times')

        total_uses = sum(tech.total_uses for tech in self.tech_classes)
        total_time = sum(tech.total_time for tech in self.tech_classes)
        avg_time = total_time / total_uses * 10 ** 6
        output.append(f'TOTAL USES: {total_uses}, {round(avg_time)}??s per')

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
