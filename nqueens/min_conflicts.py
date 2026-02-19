"""
Pure min-conflicts local search for N-Queens (iterative only).

- Random start (one queen per row; random permutation => one per column)
- Min-conflicts move: pick a conflicted row, move queen to a minimum-conflict column
- Random restarts + noisy moves to escape plateaus

Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

import random

from nqueens.csp_state import NQueensState


def _random_restart(state: NQueensState) -> None:
    state.board = random.sample(range(state.n), state.n)
    state.col_count = [0] * state.n
    state.diag1_count = [0] * (2 * state.n)
    state.diag2_count = [0] * (2 * state.n)
    state._build_counters()


def _best_columns_for_row(state: NQueensState, row: int) -> tuple[int, list[int]]:
    """Return the minimum conflict value for a row and all columns that achieve it."""
    min_conf = float("inf")
    best_cols: list[int] = []
    for col in range(state.n):
        conf = state.conflicts(row, col)
        if conf < min_conf:
            min_conf = conf
            best_cols = [col]
        elif conf == min_conf:
            best_cols.append(col)
    return int(min_conf), best_cols


def solve_min_conflicts(state: NQueensState, max_steps: int = 100_000) -> bool:
    """
    Solve N-Queens using *pure* min-conflicts (iterative local search).

    Returns True if a solution is found before max_steps, else False.
    """
    sample_size = min(30, state.n)
    stagnation_limit = max(120, state.n * 6)
    max_restarts = max(3, min(40, max_steps // max(1, stagnation_limit)))

    restarts = 0
    best_conflicted = state.n + 1
    stagnant_steps = 0

    for _ in range(max_steps):
        conflicted_rows = [
            r for r in range(state.n)
            if state.conflicts(r, state.board[r]) > 0
        ]
        if not conflicted_rows:
            return True

        # 2) Track progress / stagnation
        conflicted_count = len(conflicted_rows)
        if conflicted_count < best_conflicted:
            best_conflicted = conflicted_count
            stagnant_steps = 0
        else:
            stagnant_steps += 1

        # 3) Plateau handling: restart, otherwise do a noisy move
        if stagnant_steps >= stagnation_limit:
            if restarts < max_restarts:
                _random_restart(state)
                restarts += 1
                best_conflicted = state.n + 1
                stagnant_steps = 0
                continue

            noisy_row = random.choice(conflicted_rows)
            _, best_cols = _best_columns_for_row(state, noisy_row)
            choices = [c for c in best_cols if c != state.board[noisy_row]]
            if not choices:
                choices = [c for c in range(state.n) if c != state.board[noisy_row]]
            state.move_queen(noisy_row, random.choice(choices))
            stagnant_steps = 0
            continue

        # 4) Pick a row to move (sample to keep cost low for large n)
        sampled_rows = random.sample(conflicted_rows, k=min(sample_size, len(conflicted_rows)))

        # Heuristic: among sampled rows, pick the one with highest current conflicts.
        # Tie-break randomly.
        row_conf_pairs = [(state.conflicts(r, state.board[r]), r) for r in sampled_rows]
        max_conf = max(c for c, _ in row_conf_pairs)
        candidate_rows = [r for c, r in row_conf_pairs if c == max_conf]
        row = random.choice(candidate_rows)
        _, best_cols = _best_columns_for_row(state, row)
        best_alt = [c for c in best_cols if c != state.board[row]]
        new_col = random.choice(best_alt if best_alt else best_cols)

        if new_col == state.board[row]:
            candidates = [c for c in range(state.n) if c != state.board[row]]
            if candidates:
                new_col = min(candidates, key=lambda c: (state.conflicts(row, c), c))

        state.move_queen(row, new_col)

    return False
