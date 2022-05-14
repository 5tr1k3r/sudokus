from collections import Counter
from typing import List, Set, Tuple

from models.tech.base_tech import BaseTechnique

NumSet = Set[int]
IndexSet = Set[Tuple[int, int]]


class HiddenSingle(BaseTechnique):
    def apply(self):
        if self.puzzle.is_solved():
            print('Puzzle is solved already')
            return True

        print(f'Applying {self.__class__.__name__} technique')

        is_progress = False

        for group in (
                self.puzzle.get_all_row_indices(),
                self.puzzle.get_all_column_indices(),
                self.puzzle.get_all_box_indices()
        ):
            group_progress = self.find_hidden_single(group)
            is_progress = group_progress or is_progress

        return is_progress

    def find_hidden_single(self, group: List[IndexSet]) -> bool:
        is_progress = False
        for indices in group:
            counter = Counter()

            for x, y in indices:
                counter.update(self.puzzle.candidates[y][x])

            for value, count in counter.items():
                if count == 1:
                    for x, y in indices:
                        if value in self.puzzle.candidates[y][x]:
                            self.assign_value_to_cell(value, x, y)
                            is_progress = True

        return is_progress
