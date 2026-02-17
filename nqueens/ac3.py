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


def revise(domains: list[set[int]], xi: int, xj: int) -> bool:
    """
    Remove unsupported values from domain(xi) with respect to xj.

    A value in xi is removed if there is no compatible value in xj.
    Returns True when at least one value is removed.
    """
    revised = False
    to_remove: list[int] = []

    for value_i in domains[xi]:
        has_support = any(
            queens_compatible(xi, value_i, xj, value_j)
            for value_j in domains[xj]
        )
        if not has_support:
            to_remove.append(value_i)

    for value in to_remove:
        domains[xi].remove(value)
        revised = True

    return revised


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
