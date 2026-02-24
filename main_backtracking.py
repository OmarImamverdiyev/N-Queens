"""
Command-line entry point for N-Queens backtracking CSP solver.

Runs exact CSP backtracking with MRV, AC-3 propagation, LCV ordering,
and deterministic tie-breaking.
"""

import argparse
import random

from nqueens.backtracking import solve_backtracking_ac3
from nqueens.io_utils import read_input
from nqueens.utils import is_valid


def main() -> None:
    """Parse CLI options, run backtracking solver, and print the result."""
    parser = argparse.ArgumentParser(
        description=(
            "Solve N-Queens using backtracking CSP with MRV + AC-3 + LCV + tie-break."
        ),
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--n",
        type=int,
        help="Board size for solving (10 <= n <= 1000).",
    )
    source_group.add_argument(
        "--input-file",
        help="Path to input file (one column index per row). Used only to infer n.",
    )
    args = parser.parse_args()

    if args.input_file:
        initial_board = read_input(args.input_file)
        n = len(initial_board)
        start_board = initial_board.copy()
    else:
        initial_board = []
        n = int(args.n)
        start_board = random.sample(range(n), n)

    if not (10 <= n <= 1000):
        raise ValueError(f"n must be between 10 and 1000, got {n}")

    solved_board = solve_backtracking_ac3(n)

    print("Start state:")
    print(start_board)

    if solved_board is not None:
        print("Solution found!")
        print(solved_board)
        print("Valid:", is_valid(solved_board))
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
