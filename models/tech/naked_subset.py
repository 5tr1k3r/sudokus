from collections import Counter

from models.tech.base_tech import BaseTechnique, check_if_solved


class NakedSubset(BaseTechnique):
    # todo this only works properly for subset of length 2
    # https://www.learn-sudoku.com/naked-triplets.html
    @check_if_solved
    def apply(self) -> bool:
        is_progress = False
        for group in self.puzzle.get_all_group_indices():
            cands_list = [cands for x, y in group if (cands := self.puzzle.candidates[y][x])]
            if len(cands_list) <= 2:
                continue

            counter = Counter([frozenset(cands) for cands in cands_list])
            for cands, count in counter.items():
                if count > 1 and count == len(cands) and count != len(cands_list):
                    cands_cells = self.get_candidates_indices_by_exact_candidates(cands, group)
                    target_cells = group - cands_cells
                    for value in cands:
                        if self.remove_candidate_from_group(value, target_cells):
                            is_progress = True

        return is_progress
