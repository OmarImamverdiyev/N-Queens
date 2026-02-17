# main.py
import sys
from nqueens.csp import NQueensCSP
from nqueens.io_utils import read_input
from nqueens.utils import is_valid


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    initial_board = read_input(input_file)
    n = len(initial_board)

    solver = NQueensCSP(n, initial_board)

    if solver.solve():
        print("Solution found!")
        print(solver.board)
        print("Valid:", is_valid(solver.board))
    else:
        print("No solution found within step limit.")


if __name__ == "__main__":
    main()
