from itertools import combinations

from models.tech.base_tech import BaseTechnique, check_if_solved


class HiddenSubset(BaseTechnique):
    @check_if_solved
    def apply(self) -> bool:
        is_progress = False
        for group in self.puzzle.get_all_group_indices():
            cands_list = [cands for x, y in group if (cands := self.puzzle.candidates[y][x])]
            if len(cands_list) <= 2:
                continue

            all_cand_values = {cand_value for cands in cands_list for cand_value in cands}
            for cand_count in range(2, 5):  # should not be 5 here but atm dunno how else.
                if len(cands_list) <= cand_count:
                    continue

                for combo in combinations(cands_list, cand_count):
                    combo_values = {n for s in combo for n in s}
                    the_rest = [x for x in cands_list]
                    for one in combo:
                        the_rest.remove(one)
                    the_rest_values = {n for s in the_rest for n in s}
                    target_values = all_cand_values - the_rest_values
                    if len(target_values) == cand_count:
                        values_to_remove = combo_values - target_values
                        if not values_to_remove:
                            continue

                        # print(f"  Hidden {('Pair', 'Triple', 'Quad')[cand_count - 2]} spotted!")
                        target_cells = {cells for x in target_values
                                        for cells in self.get_candidates_indices_by_value(x, group)}
                        for value in values_to_remove:
                            if self.remove_candidate_from_group(value, target_cells):
                                is_progress = True

        return is_progress
