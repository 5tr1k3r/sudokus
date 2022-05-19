from collections import defaultdict
from itertools import combinations
from typing import Callable, Tuple

from models.puzzle import (get_all_row_indices, get_all_column_indices,
                           get_row_indices, get_column_indices,
                           get_row_indices_by_xy, get_column_indices_by_xy)
from models.tech.base_tech import BaseTechnique, check_if_solved

Index = Tuple[int, int]


class XWing(BaseTechnique):
    @check_if_solved
    def apply(self) -> bool:
        row_progress = self.find_xwing_in_groups(get_all_row_indices, get_row_indices, get_column_indices_by_xy)
        col_progress = self.find_xwing_in_groups(get_all_column_indices, get_column_indices, get_row_indices_by_xy,)

        return row_progress or col_progress

    def find_xwing_in_groups(self, get_all_groups_func: Callable,
                             main_group_func: Callable,
                             secondary_group_func: Callable) -> bool:
        progress = False
        s = self.puzzle.size
        values_and_groups = defaultdict(set)
        for i, group in enumerate(get_all_groups_func(s)):
            counter = self.get_candidates_counter(group)
            for value in {value for value, count in counter.items() if count == 2}:
                values_and_groups[i].add(value)

        for (a_group, a_value), (b_group, b_value) in combinations(values_and_groups.items(), 2):
            common_values = a_value & b_value
            if not common_values:
                continue

            for value in common_values:
                group = main_group_func(s, a_group) | main_group_func(s, b_group)
                cells = sorted(cell for cell in self.get_candidates_indices_by_value(value, group))
                if len(cells) != 4:
                    continue

                if self.is_rectangle(*cells):
                    target_cells = ((secondary_group_func(s, *cells[0]) |
                                    secondary_group_func(s, *cells[3])) - set(cells))
                    if self.remove_candidate_from_group(value, target_cells):
                        progress = True

        return progress

    @staticmethod
    def is_rectangle(a: Index, b: Index, c: Index, d: Index) -> bool:
        return a[0] == b[0] and c[0] == d[0] and a[1] == c[1] and b[1] == d[1]
