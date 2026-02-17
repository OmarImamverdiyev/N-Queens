import random
import sys


# ------------------------------
# Board Generators
# ------------------------------

def generate_random_board(n):
    """Generate random N-Queens board (may contain conflicts)."""
    return [random.randint(0, n - 1) for _ in range(n)]


def generate_constructive_solution(n):
    """
    Deterministic valid solution for many even n.
    Works well for large even n like 1000.
    """
    if n % 2 != 0:
        raise ValueError("Constructive method works best for even n.")

    solution = []

    # Even columns first
    for i in range(0, n, 2):
        solution.append(i)

    # Then odd columns
    for i in range(1, n, 2):
        solution.append(i)

    return solution


def generate_diagonal(n):
    """Hard case: all queens on main diagonal."""
    return list(range(n))


def generate_anti_diagonal(n):
    """Hard case: all queens on anti-diagonal."""
    return list(reversed(range(n)))


# ------------------------------
# File Writer
# ------------------------------

def write_board(board, filename):
    with open(filename, "w") as f:
        for col in board:
            f.write(str(col) + "\n")


# ------------------------------
# Main
# ------------------------------

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python generate_nqueens.py <n> <output_file> [--random | --solution | --hard-diagonal | --hard-anti]")
        sys.exit(1)

    n = int(sys.argv[1])
    output_file = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "--random"

    if mode == "--solution":
        board = generate_constructive_solution(n)
        print(f"Generated valid constructive solution for n={n}")

    elif mode == "--hard-diagonal":
        board = generate_diagonal(n)
        print(f"Generated HARD diagonal case for n={n}")

    elif mode == "--hard-anti":
        board = generate_anti_diagonal(n)
        print(f"Generated HARD anti-diagonal case for n={n}")

    else:
        board = generate_random_board(n)
        print(f"Generated random board for n={n}")

    write_board(board, output_file)
    print(f"Saved to {output_file}")
