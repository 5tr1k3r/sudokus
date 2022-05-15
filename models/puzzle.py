from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple

import pyperclip

NumSet = Set[int]
IndexSet = Set[Tuple[int, int]]


class Puzzle:
    supported_sizes: Dict[int, int] = {4: 2, 9: 3, 16: 4}

    def __init__(self, size: int = 9, grid: List[List[int]] = None):
        """Represents a sudoku puzzle.

        Grids that are supported: 9x9, 4x4 and 16x16.
        Supported block sizes are 3x3, 2x2 and 4x4, respectively.
        Supply a grid object or don't supply anything and make an empty grid.

        :param size: width and height as a single number (4, 9 or 16)
        :param grid: a grid object to be used, optional
        """
        if size not in self.supported_sizes:
            raise ValueError(f'Invalid puzzle: unsupported puzzle size ({size})')

        self.size = size
        self.box_size = self.supported_sizes[size]
        if grid is None:
            self.grid: List[List[int]] = [[0 for _ in range(self.size)] for _ in range(self.size)]
        else:
            self.grid = grid

        self.candidates: List[List[NumSet]] = self.get_all_candidates()
        self.original_clue_count = self.count_cells()
        self.is_solved = False

    @classmethod
    def from_file(cls, filename: str) -> Optional['Puzzle']:
        """Load a puzzle from a file.

        Format: each cell is separated by whitespace, each row is on a separate line.
        Unknown cells are marked by `x` or any other character.
        Example of a 4x4 puzzle file:

        | 1 x x 4
        | 3 x x x
        | x x 4 x
        | x x x 1

        All puzzle files should be placed in `puzzles` folder.

        :param filename: name of the file that contains the puzzle, excluding folder name
        :return: Instance of Puzzle or None if puzzle file doesn't exist
        """
        file = Path(__file__).parent.parent / 'puzzles' / filename
        if not file.is_file():
            print(f"{file} doesn't exist")
            return

        with open(file) as f:
            rows_list = f.read().splitlines()

        size = len(rows_list)
        if len(rows_list[0].split()) == 1:
            raise ValueError('Invalid puzzle file: whitespace between numbers is required')

        if not all(len(row.split()) == size for row in rows_list):
            raise ValueError('Invalid puzzle file: dimensions do not match')

        suitable_num_strings = {str(x) for x in range(1, size + 1)}

        def parse_num(num: str) -> int:
            return int(num) if num in suitable_num_strings else 0

        grid = [list(map(parse_num, row.split())) for row in rows_list]

        return cls(size, grid)

    @classmethod
    def from_string(cls, puzzle_string: str) -> 'Puzzle':
        """Load a puzzle from a string.

        Format: everything in one line, no spaces. Unknown cells are `0`.

        Example: 030072001000030090518000003050203100000705306000640205200060014007000630000008900

        .. note:: Only 4x4 and 9x9 puzzles are supported due to ambiguity of 16x16
            (`111` could be both `(11, 1)` and `(1, 11)`)

        :param puzzle_string: string to get puzzle grid from
        :return: Instance of Puzzle
        """
        allowed_lengths = {16: 4, 81: 9}
        puzzle_string = puzzle_string.strip()
        if (slen := len(puzzle_string)) not in allowed_lengths:
            raise ValueError(f"Invalid puzzle string: "
                             f"length should be one of {tuple(allowed_lengths)}, but it's {slen}")

        size = allowed_lengths[slen]
        try:
            grid = [[int(x) for x in puzzle_string[i * size:i * size + size]] for i in range(size)]
        except ValueError as e:
            raise ValueError('Invalid puzzle string: all characters should be digits') from e

        return cls(size, grid)

    def count_cells(self) -> int:
        return len([x for row in self.grid for x in row if x > 0])

    def check_if_solved(self) -> bool:
        if not self.is_solved:
            status = all(x for row in self.grid for x in row)
            self.is_solved = status
            return status

        return self.is_solved

    def get_puzzle_string(self) -> str:
        return ''.join(str(x) for row in self.grid for x in row)

    def copy_puzzle_string(self):
        # this should get moved to the future Game class
        pyperclip.copy(self.get_puzzle_string())
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

    def get_box_base_index(self, x: int, y: int) -> Tuple[int, int]:
        return x - x % self.box_size, y - y % self.box_size

    def get_row_indices(self, _x: int, y: int) -> IndexSet:
        return set(((x, y) for x in range(self.size)))

    def get_column_indices(self, x: int, _y: int) -> IndexSet:
        return set(((x, y) for y in range(self.size)))

    def get_box_indices(self, x: int, y: int) -> IndexSet:
        box_x, box_y = self.get_box_base_index(x, y)
        return set(((x, y) for y in range(box_y, box_y + self.box_size) for x in range(box_x, box_x + self.box_size)))

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

    def get_all_group_indices(self) -> List[IndexSet]:
        return self.get_all_row_indices() + self.get_all_column_indices() + self.get_all_box_indices()

    def get_all_rows(self) -> List[NumSet]:
        return [set(self.grid[y][x] for x, y in row) for row in self.get_all_row_indices()]

    def get_all_columns(self) -> List[NumSet]:
        return [set(self.grid[y][x] for x, y in row) for row in self.get_all_column_indices()]

    def get_all_boxes(self) -> List[NumSet]:
        return [set(self.grid[y][x] for x, y in row) for row in self.get_all_box_indices()]

    def validate_solution(self) -> bool:
        all_groups = self.get_all_rows() + self.get_all_columns() + self.get_all_boxes()
        return all(len(group) == self.size for group in all_groups)


if __name__ == '__main__':
    puzzle = Puzzle.from_file('sudoku2.txt')
    print(puzzle.candidates)
    puzzle.copy_puzzle_string()
