from models.puzzle import Puzzle
from models.tech.base_tech import BaseTechnique, check_if_solved_and_update_stats


class LockedCandidatesInBox(BaseTechnique):
    @check_if_solved_and_update_stats
    def apply(self, puzzle: Puzzle) -> bool:
        is_progress = False

        line_groups = puzzle.get_all_row_indices() + puzzle.get_all_column_indices()
        for group in line_groups:
            counter = puzzle.get_candidates_counter(group)
            for value, count in counter.items():
                # Check if there is enough of them and also not too many (2 or 3 for 9x9 grid)
                if not 2 <= count <= puzzle.box_size:
                    continue

                # Now check if they belong to the same box
                indices = puzzle.get_candidates_indices_by_value(value, group)
                if not len(set(puzzle.get_box_base_index(x, y) for x, y in indices)) == 1:
                    continue

                x, y = indices.pop()
                target_cells = puzzle.get_box_indices(x, y) - group
                if puzzle.remove_candidate_from_group(value, target_cells):
                    is_progress = True

        return is_progress
