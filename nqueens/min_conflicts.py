"""
Min-conflicts search for N-Queens.

Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

import random

from nqueens.ac3 import ac3, queens_compatible
from nqueens.csp_state import NQueensState


def _random_restart(state: NQueensState) -> None:
    """Reset state to a random one-queen-per-column board."""
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
        conflicts = state.conflicts(row, col)
        if conflicts < min_conf:
            min_conf = conflicts
            best_cols = [col]
        elif conflicts == min_conf:
            best_cols.append(col)
    return int(min_conf), best_cols


def _row_lcv_impact(state: NQueensState, row: int, col: int) -> int:
    """
    Approximate how constraining placing (row, col) is for other rows.

    Lower is better (LCV).
    """
    impact = 0
    for other_row in range(state.n):
        if other_row == row:
            continue
        other_col = state.board[other_row]
        if other_col == col or abs(other_col - col) == abs(other_row - row):
            impact += 1
    return impact


def _build_domains_from_state(state: NQueensState, rows: list[int]) -> list[set[int]]:
    """
    Build row domains from current board and propagate with AC-3.

    For each active row, domain is initialized from minimum-conflict columns.
    """
    domains = [set(range(state.n)) for _ in range(state.n)]

    for row in rows:
        _, best_cols = _best_columns_for_row(state, row)
        domains[row] = set(best_cols)

    ac3(domains, active_rows=rows)

    # If propagation empties a row domain, recover with minimum-conflict values
    # to keep iterative search moving instead of stalling.
    for row in rows:
        if domains[row]:
            continue
        _, best_cols = _best_columns_for_row(state, row)
        domains[row] = set(best_cols)

    return domains


def _lcv_order_from_domains(
    row: int,
    domains: list[set[int]],
    active_rows: list[int],
) -> list[int]:
    """Order domain values for a row using LCV, then column tie-break."""

    neighbors = [other for other in active_rows if other != row]

    def elimination_count(col: int) -> int:
        removed = 0
        for other_row in neighbors:
            for other_col in domains[other_row]:
                if not queens_compatible(row, col, other_row, other_col):
                    removed += 1
        return removed

    return sorted(domains[row], key=lambda col: (elimination_count(col), col))


def solve_min_conflicts(state: NQueensState, max_steps: int = 100_000) -> bool:
    """
    Solve N-Queens using the min-conflicts heuristic.

    Returns `True` if a solution is found before `max_steps`, otherwise `False`.
    """
    # Small sample keeps per-step cost practical for n up to 1000 while
    # still applying MRV + tie-breaking + AC-3.
    sample_size = min(30, state.n)
    stagnation_limit = max(120, state.n * 6)
    max_restarts = max(3, min(40, max_steps // max(1, stagnation_limit)))
    restarts = 0
    best_conflicted = state.n + 1
    stagnant_steps = 0

    for _ in range(max_steps):
        conflicted_rows = [
            row for row in range(state.n)
            if state.conflicts(row, state.board[row]) > 0
        ]

        if not conflicted_rows:
            return True

        conflicted_count = len(conflicted_rows)
        if conflicted_count < best_conflicted:
            best_conflicted = conflicted_count
            stagnant_steps = 0
        else:
            stagnant_steps += 1

        if stagnant_steps >= stagnation_limit:
            if restarts < max_restarts:
                _random_restart(state)
                restarts += 1
                best_conflicted = state.n + 1
                stagnant_steps = 0
                continue

            # If restart budget is exhausted, force a noisy move to escape plateau.
            noisy_row = random.choice(conflicted_rows)
            _, best_cols = _best_columns_for_row(state, noisy_row)
            choices = [col for col in best_cols if col != state.board[noisy_row]]
            if not choices:
                choices = [col for col in range(state.n) if col != state.board[noisy_row]]
            state.move_queen(noisy_row, random.choice(choices))
            stagnant_steps = 0
            continue

        # MRV heuristic: among sampled conflicted rows, pick row with the fewest
        # propagated domain values. Tie-break by larger current conflict count.
        sampled_rows = random.sample(
            conflicted_rows,
            k=min(sample_size, len(conflicted_rows)),
        )

        domains = _build_domains_from_state(state, sampled_rows)

        row_candidates: list[tuple[int, int, int]] = []
        for row in sampled_rows:
            current_conf = state.conflicts(row, state.board[row])
            domain_size = len(domains[row]) if domains[row] else state.n + 1
            row_candidates.append((domain_size, -current_conf, row))

        row_candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        best_domain_size = row_candidates[0][0]
        best_conflict_tie = row_candidates[0][1]
        tied_rows = [
            item for item in row_candidates
            if item[0] == best_domain_size and item[1] == best_conflict_tie
        ]
        _, _, row = random.choice(tied_rows)

        if domains[row]:
            value_order = _lcv_order_from_domains(row, domains, sampled_rows)
            new_col = value_order[0]
        else:
            # Fallback when propagation makes domain empty in sampled scope.
            _, best_cols = _best_columns_for_row(state, row)
            new_col = min(best_cols, key=lambda col: (_row_lcv_impact(state, row, col), col))

        if new_col == state.board[row] and len(domains[row]) > 1:
            for col in _lcv_order_from_domains(row, domains, sampled_rows):
                if col != state.board[row]:
                    new_col = col
                    break
        elif new_col == state.board[row]:
            # Sideways move fallback when domain offers no alternative.
            fallback = sorted(
                (col for col in range(state.n) if col != state.board[row]),
                key=lambda col: (state.conflicts(row, col), _row_lcv_impact(state, row, col), col),
            )
            if fallback:
                new_col = fallback[0]

        state.move_queen(row, new_col)

    return False
