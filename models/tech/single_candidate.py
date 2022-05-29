from models.puzzle import Puzzle
from models.tech.base_tech import BaseTechnique, check_if_solved_and_update_stats


class SingleCandidate(BaseTechnique):
    @check_if_solved_and_update_stats
    def apply(self, puzzle: Puzzle) -> bool:
        is_progress = False
        for y in range(puzzle.size):
            for x in range(puzzle.size):
                if len(cands := puzzle.candidates[y][x]) == 1:
                    found_value = cands.pop()
                    puzzle.assign_value_to_cell(found_value, x, y)
                    is_progress = True

        return is_progress
