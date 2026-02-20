"""
AC-3 constraint propagation for N-Queens.

Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

from __future__ import annotations

from collections import deque


def queens_compatible(row_i: int, col_i: int, row_j: int, col_j: int) -> bool:
    """Return True if two queens do not attack each other."""
    if col_i == col_j:
        return False
    if abs(col_i - col_j) == abs(row_i - row_j):
        return False
    return True


def _value_has_support(value_i: int, domain_j: set[int], row_distance: int) -> bool:
    """
    Fast support check for N-Queens arc constraints.

    For fixed rows `xi` and `xj`, a value `value_i` is incompatible with at most
    three values in `domain_j`: same column and two diagonals.
    """
    if not domain_j:
        return False

    # At most 3 values can be forbidden; larger domains must contain support.
    if len(domain_j) > 3:
        return True

    banned_same = value_i
    banned_diag_up = value_i + row_distance
    banned_diag_down = value_i - row_distance

    for value_j in domain_j:
        if value_j != banned_same and value_j != banned_diag_up and value_j != banned_diag_down:
            return True

    return False


def revise(domains: list[set[int]], xi: int, xj: int) -> bool:
    """
    Remove unsupported values from domain(xi) with respect to xj.

    A value in xi is removed if there is no compatible value in xj.
    Returns True when at least one value is removed.
    """
    domain_i = domains[xi]
    domain_j = domains[xj]
    row_distance = abs(xi - xj)

    to_remove = [
        value_i for value_i in domain_i
        if not _value_has_support(value_i, domain_j, row_distance)
    ]
    if not to_remove:
        return False

    domain_i.difference_update(to_remove)
    return True


def ac3(
    domains: list[set[int]],
    active_rows: list[int] | None = None,
    initial_queue: list[tuple[int, int]] | None = None,
) -> bool:
    """
    Enforce arc consistency on the provided domains.

    Returns True if all domains remain non-empty, otherwise False.
    """
    if active_rows is None:
        active_rows = list(range(len(domains)))

    active = set(active_rows)

    if initial_queue is None:
        queue = deque(
            (xi, xj)
            for xi in active_rows
            for xj in active_rows
            if xi != xj
        )
    else:
        queue = deque(initial_queue)

    while queue:
        xi, xj = queue.popleft()
        if xi not in active or xj not in active:
            continue

        if revise(domains, xi, xj):
            if not domains[xi]:
                return False

            for xk in active_rows:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))

    return True
