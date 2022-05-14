from models.tech.base_tech import BaseTechnique, check_if_solved


class LockedCandidatesInBox(BaseTechnique):
    @check_if_solved
    def apply(self) -> bool:
        is_progress = False

        line_groups = self.puzzle.get_all_row_indices() + self.puzzle.get_all_column_indices()
        for group in line_groups:
            counter = self.get_candidates_counter(group)
            for value, count in counter.items():
                # Check if there is enough of them and also not too many (2 or 3 for 9x9 grid)
                if not 2 <= count <= self.puzzle.box_size:
                    continue

                # Now check if they belong to the same box
                indices = self.get_candidates_indices_by_value(value, group)
                if not len(set(self.puzzle.get_box_base_index(x, y) for x, y in indices)) == 1:
                    continue

                x, y = indices.pop()
                target_cells = self.puzzle.get_box_indices(x, y) - group
                removed_count = self.remove_candidate_from_group(value, target_cells)
                if removed_count > 0:
                    is_progress = True

        return is_progress
