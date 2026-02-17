import argparse

from nqueens.csp import NQueensCSP
from nqueens.io_utils import read_input
from nqueens.utils import is_valid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Solve N-Queens from an input board file.",
    )
    parser.add_argument("input_file", help="Path to input file (one column index per row).")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=100_000,
        help="Maximum iterative steps for project solver.",
    )
    args = parser.parse_args()

    initial_board = read_input(args.input_file)
    n = len(initial_board)
    if not (10 <= n <= 1000):
        raise ValueError(f"n must be between 10 and 1000, got {n}")

    solver = NQueensCSP(n, initial_board)

    if solver.solve(max_steps=args.max_steps):
        print("Solution found!")
        print(solver.board)
        print("Valid:", is_valid(solver.board))
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
