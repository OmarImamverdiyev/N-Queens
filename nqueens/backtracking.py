"""
Backtracking CSP solver with MRV, LCV, tie-breaking, and AC-3.

@Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

from nqueens.ac3 import ac3, queens_compatible


def _select_unassigned_row(
    domains: list[set[int]],
    assigned: set[int],
    n: int,
) -> int:
    """
    Choose the next row using MRV, then a deterministic tie-break.

    Tie-break rule:
    - smaller domain size (MRV)
    - then smaller row index for reproducibility
    """
    candidates = [row for row in range(n) if row not in assigned]
    return min(candidates, key=lambda row: (len(domains[row]), row))


def _lcv_order(
    row: int,
    domains: list[set[int]],
    assigned: set[int],
    n: int,
) -> list[int]:
    """
    Sort values by Least Constraining Value (LCV).

    A value is better when it removes fewer values from neighbors.
    """
    unassigned_neighbors = [r for r in range(n) if r not in assigned and r != row]

    def elimination_count(col: int) -> int:
        """Count how many neighbor-domain values become invalid for `col`."""
        removed = 0
        for other_row in unassigned_neighbors:
            for other_col in domains[other_row]:
                if not queens_compatible(row, col, other_row, other_col):
                    removed += 1
        return removed

    return sorted(domains[row], key=lambda col: (elimination_count(col), col))


def _backtrack(
    domains: list[set[int]],
    assigned: set[int],
    n: int,
) -> list[int] | None:
    """Recursively assign rows using MRV/LCV with AC-3 propagation."""
    if len(assigned) == n:
        return [next(iter(domains[row])) for row in range(n)]

    row = _select_unassigned_row(domains, assigned, n)

    for col in _lcv_order(row, domains, assigned, n):
        new_domains = [domain.copy() for domain in domains]
        new_domains[row] = {col}

        # AC-3 propagation triggered from this assignment.
        queue = [(other, row) for other in range(n) if other != row]
        if ac3(new_domains, active_rows=list(range(n)), initial_queue=queue):
            new_assigned = assigned.copy()
            new_assigned.add(row)

            result = _backtrack(new_domains, new_assigned, n)
            if result is not None:
                return result

    return None


def solve_backtracking_ac3(n: int) -> list[int] | None:
    """
    Solve N-Queens by CSP backtracking + AC-3.

    This method is exact but expensive for large n.
    """
    domains = [set(range(n)) for _ in range(n)]
    if not ac3(domains):
        return None
    return _backtrack(domains, assigned=set(), n=n)
