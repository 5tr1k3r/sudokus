from models.tech.base_tech import BaseTechnique


class SingleCandidate(BaseTechnique):
    def apply(self) -> bool:
        if self.puzzle.is_solved():
            print('Puzzle is solved already')
            return True

        print(f'Applying {self.__class__.__name__} technique')

        is_progress = False
        for y in range(self.puzzle.size):
            for x in range(self.puzzle.size):
                if len(cands := self.puzzle.candidates[y][x]) == 1:
                    found_value = cands.pop()
                    print(f'{found_value=} at position {x, y}')

                    self.puzzle.grid[y][x] = found_value
                    self.puzzle.remove_candidate_from_rcb(found_value, x, y)
                    is_progress = True

        return is_progress
