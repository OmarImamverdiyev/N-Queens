"""
Min-conflicts search for N-Queens.

Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

import random

from nqueens.ac3 import ac3
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


def _cap_domain_values(
    state: NQueensState,
    row: int,
    values: list[int],
    domain_cap: int,
) -> set[int]:
    """Deterministically cap a row domain to keep propagation cheap."""
    if len(values) <= domain_cap:
        return set(values)

    current_col = state.board[row]
    trimmed = sorted(values, key=lambda col: (abs(col - current_col), col))
    return set(trimmed[:domain_cap])


def _build_domains_from_state(
    state: NQueensState,
    rows: list[int],
    domain_cap: int,
    use_ac3: bool,
) -> list[set[int]]:
    """
    Build row domains from current board and propagate with AC-3.

    For each active row, domain is initialized from minimum-conflict columns.
    """
    domains = [set(range(state.n)) for _ in range(state.n)]

    for row in rows:
        _, best_cols = _best_columns_for_row(state, row)
        domains[row] = _cap_domain_values(state, row, best_cols, domain_cap)

    if use_ac3 and len(rows) > 1:
        ac3(domains, active_rows=rows)

    # If propagation empties a row domain, recover with minimum-conflict values
    # to keep iterative search moving instead of stalling.
    for row in rows:
        if domains[row]:
            continue
        _, best_cols = _best_columns_for_row(state, row)
        domains[row] = _cap_domain_values(state, row, best_cols, domain_cap)

    return domains


def _lcv_order_from_domains(
    row: int,
    domains: list[set[int]],
    active_rows: list[int],
) -> list[int]:
    """Order domain values for a row using LCV, then column tie-break."""

    neighbors = [other for other in active_rows if other != row]

    def elimination_count(col: int) -> int:
        # For each neighbor row, at most 3 values are ruled out:
        # same column, and two diagonal columns.
        removed = 0
        for other_row in neighbors:
            other_domain = domains[other_row]
            row_distance = abs(other_row - row)
            if col in other_domain:
                removed += 1
            if col + row_distance in other_domain:
                removed += 1
            if col - row_distance in other_domain:
                removed += 1
        return removed

    return sorted(domains[row], key=lambda col: (elimination_count(col), col))


def solve_min_conflicts(state: NQueensState, max_steps: int = 100_000) -> bool:
    """
    Solve N-Queens using the min-conflicts heuristic.

    Returns `True` if a solution is found before `max_steps`, otherwise `False`.
    """
    # Adaptive settings keep per-step work bounded for larger n while
    # preserving MRV/LCV/AC-3 behavior.
    if state.n >= 400:
        sample_size = min(8, state.n)
        domain_cap = min(6, state.n)
        ac3_period = 6
        stagnation_limit = max(80, state.n // 2)
    elif state.n >= 100:
        sample_size = min(12, state.n)
        domain_cap = min(8, state.n)
        ac3_period = 4
        stagnation_limit = max(100, state.n)
    else:
        sample_size = min(30, state.n)
        domain_cap = min(12, state.n)
        ac3_period = 1
        stagnation_limit = max(120, state.n * 6)

    max_restarts = max(4, min(60, max_steps // max(1, stagnation_limit)))
    restarts = 0
    best_conflicted = state.n + 1
    stagnant_steps = 0

    for step in range(max_steps):
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

        should_propagate = (
            step % ac3_period == 0
            or stagnant_steps >= max(8, ac3_period * 2)
        )
        domains = _build_domains_from_state(
            state,
            sampled_rows,
            domain_cap=domain_cap,
            use_ac3=should_propagate,
        )

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
            new_col = min(
                best_cols,
                key=lambda col: (abs(col - state.board[row]), col),
            )

        if new_col == state.board[row] and len(domains[row]) > 1:
            for col in _lcv_order_from_domains(row, domains, sampled_rows):
                if col != state.board[row]:
                    new_col = col
                    break
        elif new_col == state.board[row]:
            # Sideways move fallback when domain offers no alternative.
            best_conflict = float("inf")
            fallback_cols: list[int] = []
            current_col = state.board[row]
            for col in range(state.n):
                if col == current_col:
                    continue
                col_conflict = state.conflicts(row, col)
                if col_conflict < best_conflict:
                    best_conflict = col_conflict
                    fallback_cols = [col]
                elif col_conflict == best_conflict:
                    fallback_cols.append(col)

            if fallback_cols:
                new_col = min(
                    fallback_cols,
                    key=lambda col: (abs(col - current_col), col),
                )

        state.move_queen(row, new_col)

    return False
