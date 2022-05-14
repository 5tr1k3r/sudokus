from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple

import pyperclip

NumSet = Set[int]
IndexSet = Set[Tuple[int, int]]


class Puzzle:
    def __init__(self, filename: Optional[str] = None):
        """
        Represents a sudoku puzzle.
        Grid sizes that are supported: 9x9, 4x4 and 16x16.
        Supported block sizes are 3x3, 2x2 and 4x4, respectively.

        :param filename: name of the file that contains the puzzle (optional)
        """
        self.supported_sizes: Dict[int, int] = {4: 2, 9: 3, 16: 4}
        self.size = 9
        self.box_size = self.find_box_size()
        self.grid: List[List[int]] = [[0 for _ in range(self.size)] for _ in range(self.size)]
        if filename is not None:
            self.load_from_file(filename)

        self.candidates: List[List[NumSet]] = self.get_all_candidates()
        self.original_clue_count = self.count_cells()

    def find_box_size(self) -> int:
        return self.supported_sizes[self.size]

    def count_cells(self) -> int:
        return len([x for row in self.grid for x in row if x > 0])

    def load_from_file(self, filename: str):
        file = Path(__file__).parent.parent / 'puzzles' / filename
        if not file.is_file():
            print(f"{file} doesn't exist")
            return

        with open(file) as f:
            rows_list = f.read().splitlines()

        self.size = len(rows_list)
        if self.size not in self.supported_sizes:
            raise RuntimeError(f'Invalid puzzle: unsupported puzzle size ({self.size})')

        if len(rows_list[0].split()) == 1:
            raise RuntimeError('Invalid puzzle: whitespace between numbers is required')

        if not all(len(row.split()) == self.size for row in rows_list):
            raise RuntimeError('Invalid puzzle: dimensions do not match')

        self.box_size = self.find_box_size()
        suitable_num_strings = {str(x) for x in range(1, self.size + 1)}

        def parse_num(num: str) -> int:
            return int(num) if num in suitable_num_strings else 0
            # return int(num)

        self.grid = [list(map(parse_num, row.split())) for row in rows_list]

    def is_solved(self) -> bool:
        return all(x for row in self.grid for x in row)

    def copy_puzzle_string(self):
        pyperclip.copy(''.join(' ' if x == 0 else str(x) for row in self.grid for x in row).rstrip())
        print('Copied the puzzle string')

    def get_all_candidates(self) -> List[List[NumSet]]:
        candidates = []
        for y in range(self.size):
            candidates.append([])
            for x in range(self.size):
                if self.grid[y][x] == 0:
                    cands = self.get_candidates_for_cell(x, y)
                else:
                    cands = set()

                candidates[y].append(cands)

        return candidates

    def get_row_indices(self, _x: int, y: int) -> IndexSet:
        return set(((x, y) for x in range(self.size)))

    def get_column_indices(self, x: int, _y: int) -> IndexSet:
        return set(((x, y) for y in range(self.size)))

    def get_box_indices(self, x: int, y: int) -> IndexSet:
        bs = self.box_size
        box_x = x // bs * bs
        box_y = y // bs * bs

        return set(((x, y) for y in range(box_y, box_y + bs) for x in range(box_x, box_x + bs)))

    def get_rcb_indices(self, x: int, y: int) -> IndexSet:
        # Get a combined set of indices from row, column and box
        return self.get_row_indices(x, y) | self.get_column_indices(x, y) | self.get_box_indices(x, y)

    def get_row(self, x: int, y: int) -> NumSet:
        return set(self.grid[j][i] for i, j in self.get_row_indices(x, y))

    def get_column(self, x: int, y: int) -> NumSet:
        return set(self.grid[j][i] for i, j in self.get_column_indices(x, y))

    def get_box(self, x: int, y: int) -> NumSet:
        return set(self.grid[j][i] for i, j in self.get_box_indices(x, y))

    def get_rcb(self, x: int, y: int) -> NumSet:
        # Get a combined set of values from row, column and box
        return set(self.grid[j][i] for i, j in self.get_rcb_indices(x, y))

    def get_candidates_for_cell(self, x: int, y: int) -> NumSet:
        return set(range(1, self.size + 1)) - self.get_rcb(x, y)

    def remove_candidate_from_rcb(self, candidate: int, x: int, y: int):
        for i, j in self.get_rcb_indices(x, y):
            self.candidates[j][i].discard(candidate)

    def get_all_row_indices(self) -> List[IndexSet]:
        return [self.get_row_indices(0, y) for y in range(self.size)]

    def get_all_column_indices(self) -> List[IndexSet]:
        return [self.get_column_indices(x, 0) for x in range(self.size)]

    def get_all_box_indices(self) -> List[IndexSet]:
        result = []
        for y in range(0, self.size, self.box_size):
            for x in range(0, self.size, self.box_size):
                result.append(self.get_box_indices(x, y))

        return result

    def show_all_candidates(self):
        for y in range(self.size):
            for x in range(self.size):
                num = self.grid[y][x]
                if num == 0:
                    a = sorted(self.get_candidates_for_cell(x, y))
                    print(x, y, a, end=' | ')
            print()

    def prettyprint_grid(self):
        for row in self.grid:
            print(row)


if __name__ == '__main__':
    puzzle = Puzzle('sudoku2.txt')
    print(puzzle.candidates)
