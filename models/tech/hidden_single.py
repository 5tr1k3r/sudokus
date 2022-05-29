from models.puzzle import Puzzle
from models.tech.base_tech import BaseTechnique, check_if_solved_and_update_stats


class HiddenSingle(BaseTechnique):
    @check_if_solved_and_update_stats
    def apply(self, puzzle: Puzzle):
        is_progress = False
        for group in puzzle.get_all_group_indices():
            counter = puzzle.get_candidates_counter(group)
            for value, count in counter.items():
                if count == 1:
                    for x, y in puzzle.get_candidates_indices_by_value(value, group):
                        puzzle.assign_value_to_cell(value, x, y)
                        is_progress = True

        return is_progress
