from __future__ import annotations

from typing import Optional

from nqueens.ac3 import ac3, queens_compatible


def _is_consistent(row: int, col: int, assignment: list[int]) -> bool:
    for r2, c2 in enumerate(assignment):
        if c2 == -1 or r2 == row:
            continue
        if not queens_compatible(row, col, r2, c2):
            return False
    return True


def _select_unassigned_var(domains: list[set[int]], assignment: list[int]) -> int:
    """
    MRV: choose unassigned row with smallest domain size.
    Tie-break: smallest row index.
    """
    best_row = -1
    best_size = 10**18
    for r in range(len(assignment)):
        if assignment[r] != -1:
            continue
        size = len(domains[r])
        if size < best_size:
            best_size = size
            best_row = r
    return best_row


def _order_values_lcv(
    row: int,
    domains: list[set[int]],
    assignment: list[int],
    preferred_col: int | None,
) -> list[int]:
    """
    LCV ordering + optional preference:
    - Prefer trying the input-file column first (as a hint), if present in domain.
    - Then the rest by LCV (least eliminations).
    """
    n = len(assignment)
    neighbors = [r for r in range(n) if r != row and assignment[r] == -1]

    def elim_count(col: int) -> int:
        removed = 0
        for r2 in neighbors:
            for c2 in domains[r2]:
                if not queens_compatible(row, col, r2, c2):
                    removed += 1
        return removed

    ordered = sorted(domains[row], key=lambda c: (elim_count(c), c))

    # Move preferred_col to the front if it's available
    if preferred_col is not None and preferred_col in domains[row]:
        ordered = [preferred_col] + [c for c in ordered if c != preferred_col]

    return ordered


def solve_csp_mac(n: int, initial_board_hint: list[int] | None = None) -> Optional[list[int]]:
    hint = (initial_board_hint or []).copy()

    assignment = [-1] * n
    domains: list[set[int]] = [set(range(n)) for _ in range(n)]

    if not ac3(domains, active_rows=list(range(n))):
        return None

    def backtrack(domains: list[set[int]], assignment: list[int]) -> Optional[list[int]]:
        if all(v != -1 for v in assignment):
            return assignment

        row = _select_unassigned_var(domains, assignment)
        if row == -1:
            return assignment

        preferred = hint[row]
        if not (0 <= preferred < n):
            preferred = None

        for col in _order_values_lcv(row, domains, assignment, preferred):
            if not _is_consistent(row, col, assignment):
                continue

            new_assignment = assignment.copy()
            new_assignment[row] = col

            new_domains = [d.copy() for d in domains]
            new_domains[row] = {col}

            # Maintain Arc Consistency after assignment
            if not ac3(new_domains, active_rows=list(range(n))):
                continue

            res = backtrack(new_domains, new_assignment)
            if res is not None:
                return res

        return None

    return backtrack(domains, assignment)
