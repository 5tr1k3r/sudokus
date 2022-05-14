from typing import List

from models.puzzle import IndexSet
from models.tech.base_tech import BaseTechnique, check_if_solved


class HiddenSingle(BaseTechnique):
    @check_if_solved
    def apply(self):
        is_progress = False
        for group_list in (
                self.puzzle.get_all_row_indices(),
                self.puzzle.get_all_column_indices(),
                self.puzzle.get_all_box_indices()
        ):
            partial_progress = self.find_hidden_single(group_list)
            is_progress = partial_progress or is_progress

        return is_progress

    def find_hidden_single(self, group_list: List[IndexSet]) -> bool:
        is_progress = False
        for group in group_list:
            counter = self.get_candidates_counter(group)
            for value, count in counter.items():
                if count == 1:
                    for x, y in self.get_candidates_indices_by_value(value, group):
                        self.assign_value_to_cell(value, x, y)
                        is_progress = True

        return is_progress
