from models.puzzle import Puzzle


class BaseTechnique:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def apply(self):
        pass
