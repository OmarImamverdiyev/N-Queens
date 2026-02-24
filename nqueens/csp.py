"""
Backward-compatible CSP interface for N-Queens.

This wrapper keeps the old `NQueensCSP` API while delegating work to:
- `nqueens.csp_state.NQueensState` for board/counter management
- `nqueens.min_conflicts.solve_min_conflicts` for project solving logic

@Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

from nqueens.csp_state import NQueensState
from nqueens.min_conflicts import solve_min_conflicts


class NQueensCSP:
    """Compatibility class used by `main.py` and existing imports."""

    def __init__(
        self,
        n: int,
        initial_board: list[int] | None = None,
        start_mode: str = "random",
    ):
        """Create solver state and preserve startup configuration."""
        self.state = NQueensState(n=n, board=initial_board or [])
        self.n = self.state.n
        self._initial_board = (initial_board or []).copy()
        self.start_mode = start_mode

    @property
    def board(self) -> list[int]:
        """Expose board through the legacy attribute name."""
        return self.state.board

    def conflicts(self, row: int, col: int) -> int:
        """Delegate conflict calculation to state object."""
        return self.state.conflicts(row, col)

    def solve(self, max_steps: int = 100_000) -> bool:
        """
        Solve N-Queens using the project iterative CSP solver.
        """
        if self.start_mode == "input":
            self.state = NQueensState(n=self.n, board=self._initial_board)
        elif self.start_mode == "random":
            self.state = NQueensState(n=self.n, board=[])
        else:
            raise ValueError(f"Unknown start_mode: {self.start_mode!r}")
        return solve_min_conflicts(self.state, max_steps=max_steps)
