"""
Command-line entry point for the N-Queens CSP solver.

@Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""

import argparse

from nqueens.csp import NQueensCSP
from nqueens.io_utils import read_input
from nqueens.utils import is_valid


def main() -> None:
    """Parse CLI options, run the solver, and print the result."""
    parser = argparse.ArgumentParser(
        description="Solve N-Queens from either random start (given n) or an input board file.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--n",
        type=int,
        help="Board size for random-start solving (10 <= n <= 1000).",
    )
    source_group.add_argument(
        "--input-file",
        help="Path to input file (one column index per row).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=100_000,
        help="Maximum iterative steps for project solver.",
    )
    args = parser.parse_args()

    # Choose start mode from either a board file or random generation by n.
    if args.input_file:
        initial_board = read_input(args.input_file)
        n = len(initial_board)
        start_mode = "input"
    else:
        initial_board = []
        n = int(args.n)
        start_mode = "random"

    # Assignment constraint: valid board sizes are in [10, 1000].
    if not (10 <= n <= 1000):
        raise ValueError(f"n must be between 10 and 1000, got {n}")

    solver = NQueensCSP(n, initial_board, start_mode=start_mode)

    if solver.solve(max_steps=args.max_steps):
        print("Solution found!")
        print(solver.board)
        print("Valid:", is_valid(solver.board))
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
