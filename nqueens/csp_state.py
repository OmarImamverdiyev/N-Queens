"""
Core board state and conflict counters for N-Queens.

Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class NQueensState:
    """
    Represents a board where index=row and value=column.

    The class maintains three counter arrays so conflict checks are O(1):
    - `col_count[col]`: queens in each column
    - `diag1_count[row - col + n]`: queens in main diagonals
    - `diag2_count[row + col]`: queens in anti-diagonals
    """

    n: int
    board: list[int] = field(default_factory=list)
    col_count: list[int] = field(init=False)
    diag1_count: list[int] = field(init=False)
    diag2_count: list[int] = field(init=False)

    def __post_init__(self) -> None:
        if not self.board:
            # Random permutation guarantees one queen per column.
            self.board = random.sample(range(self.n), self.n)
        else:
            self.board = self.board.copy()

        self.col_count = [0] * self.n
        self.diag1_count = [0] * (2 * self.n)
        self.diag2_count = [0] * (2 * self.n)
        self._build_counters()

    def _build_counters(self) -> None:
        """Initialize all counters from the current board."""
        for row in range(self.n):
            col = self.board[row]
            self.col_count[col] += 1
            self.diag1_count[row - col + self.n] += 1
            self.diag2_count[row + col] += 1

    def conflicts(self, row: int, col: int) -> int:
        """
        Return number of conflicts if queen in `row` were placed at `col`.

        The subtraction removes this queen's own contribution when checking
        its current location.
        """
        return (
            self.col_count[col]
            + self.diag1_count[row - col + self.n]
            + self.diag2_count[row + col]
            - 3 * (self.board[row] == col)
        )

    def move_queen(self, row: int, new_col: int) -> None:
        """Move a queen and update counters incrementally."""
        old_col = self.board[row]

        self.col_count[old_col] -= 1
        self.diag1_count[row - old_col + self.n] -= 1
        self.diag2_count[row + old_col] -= 1

        self.board[row] = new_col

        self.col_count[new_col] += 1
        self.diag1_count[row - new_col + self.n] += 1
        self.diag2_count[row + new_col] += 1
