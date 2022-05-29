from models.puzzle import Puzzle
from models.tech.base_tech import BaseTechnique, check_if_solved_and_update_stats


class LockedCandidatesOnLine(BaseTechnique):
    @check_if_solved_and_update_stats
    def apply(self, puzzle: Puzzle) -> bool:
        is_progress = False
        for box in puzzle.get_all_box_indices():
            counter = puzzle.get_candidates_counter(box)
            for value, count in counter.items():
                # Check if they can form a line
                if not 2 <= count <= puzzle.box_size:
                    continue

                cands = puzzle.get_candidates_indices_by_value(value, box)
                line_is_formed = False

                # Horizontal alignment / row
                if len(set(x[1] for x in cands)) == 1:
                    line_is_formed = True
                    x, y = cands.pop()
                    target_cells = puzzle.get_row_indices(x, y) - puzzle.get_box_indices(x, y)

                # Vertical alignment / column
                elif len(set(x[0] for x in cands)) == 1:
                    line_is_formed = True
                    x, y = cands.pop()
                    target_cells = puzzle.get_column_indices(x, y) - puzzle.get_box_indices(x, y)

                if line_is_formed:
                    # noinspection PyUnboundLocalVariable
                    if puzzle.remove_candidate_from_group(value, target_cells):
                        is_progress = True

        return is_progress
