from models.tech.base_tech import BaseTechnique, check_if_solved


class LockedCandidatesOnLine(BaseTechnique):
    @check_if_solved
    def apply(self) -> bool:
        is_progress = False
        for box in self.puzzle.get_all_box_indices():
            counter = self.get_candidates_counter(box)
            for value, count in counter.items():
                # Check if they can form a line
                if not 2 <= count <= self.puzzle.box_size:
                    continue

                cands = self.get_candidates_indices_by_value(value, box)
                line_is_formed = False

                # Horizontal alignment / row
                if len(set(x[1] for x in cands)) == 1:
                    line_is_formed = True
                    x, y = cands.pop()
                    target_cells = self.puzzle.get_row_indices(x, y) - self.puzzle.get_box_indices(x, y)

                # Vertical alignment / column
                elif len(set(x[0] for x in cands)) == 1:
                    line_is_formed = True
                    x, y = cands.pop()
                    target_cells = self.puzzle.get_column_indices(x, y) - self.puzzle.get_box_indices(x, y)

                if line_is_formed:
                    # noinspection PyUnboundLocalVariable
                    if self.remove_candidate_from_group(value, target_cells):
                        is_progress = True

        return is_progress
