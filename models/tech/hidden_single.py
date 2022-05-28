from models.tech.base_tech import BaseTechnique, check_if_solved


class HiddenSingle(BaseTechnique):
    @check_if_solved
    def apply(self):
        is_progress = False
        for group in self.puzzle.get_all_group_indices():
            counter = self.get_candidates_counter(group)
            for value, count in counter.items():
                if count == 1:
                    for x, y in self.get_candidates_indices_by_value(value, group):
                        self.puzzle.assign_value_to_cell(value, x, y)
                        is_progress = True

        return is_progress
