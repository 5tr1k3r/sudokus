from models.tech.base_tech import BaseTechnique, check_if_solved


class SingleCandidate(BaseTechnique):
    @check_if_solved
    def apply(self) -> bool:
        is_progress = False
        for y in range(self.puzzle.size):
            for x in range(self.puzzle.size):
                if len(cands := self.puzzle.candidates[y][x]) == 1:
                    found_value = cands.pop()
                    self.assign_value_to_cell(found_value, x, y)
                    is_progress = True

        return is_progress
