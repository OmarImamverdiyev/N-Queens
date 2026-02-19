"""
Unified interface for N-Queens.

Modes:
- iterative: min-conflicts local search (random start)
- csp: backtracking + AC-3 propagation (MAC)

Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

from nqueens.csp_state import NQueensState
from nqueens.min_conflicts import solve_min_conflicts

from nqueens.backtracking import solve_csp_mac


class NQueensCSP:
    """Single entry-point used by main.py."""

    def __init__(self, n: int, initial_board: list[int] | None = None, mode: str = "iterative"):
        self.n = n
        self.mode = mode
        self._initial_board = (initial_board or []).copy()

        # board/state is created on solve() depending on the chosen mode
        self.state: NQueensState | None = None
        self._board: list[int] = self._initial_board.copy()

    @property
    def board(self) -> list[int]:
        if self.state is not None:
            return self.state.board
        return self._board

    def conflicts(self, row: int, col: int) -> int:
        if self.state is None:
            raise RuntimeError("conflicts() is only available in iterative mode after state is created.")
        return self.state.conflicts(row, col)

    def solve(self, max_steps: int = 100_000) -> bool:
        if self.mode == "iterative":
            self.state = NQueensState(n=self.n, board=[])
            return solve_min_conflicts(self.state, max_steps=max_steps)

        if self.mode == "csp":
            sol = solve_csp_mac(self.n, initial_board_hint=self._initial_board)
            if sol is None:
                return False
            self._board = sol
            self.state = None
            return True

        raise ValueError(f"Unknown mode: {self.mode!r}")
