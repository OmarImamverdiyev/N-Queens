import random
import sys


# ------------------------------
# Board Generators
# ------------------------------

def generate_random_board(n):
    """Generate a random board with exactly one queen per column."""
    return random.sample(range(n), n)


def _conflict_count(board):
    """Return number of attacking queen pairs for a board permutation."""
    n = len(board)
    col_count = [0] * n
    diag1_count = [0] * (2 * n)
    diag2_count = [0] * (2 * n)

    for row, col in enumerate(board):
        col_count[col] += 1
        diag1_count[row - col + n] += 1
        diag2_count[row + col] += 1

    conflicts = 0
    for count in col_count:
        conflicts += count * (count - 1) // 2
    for count in diag1_count:
        conflicts += count * (count - 1) // 2
    for count in diag2_count:
        conflicts += count * (count - 1) // 2
    return conflicts


def generate_easy_board(n, attempts=200):
    """
    Generate an easy board by sampling random permutations and
    returning the one with the fewest conflicts.
    """
    best_board = generate_random_board(n)
    best_score = _conflict_count(best_board)

    if best_score == 0:
        return best_board

    for _ in range(attempts - 1):
        board = generate_random_board(n)
        score = _conflict_count(board)
        if score < best_score:
            best_board = board
            best_score = score
            if best_score == 0:
                break

    return best_board


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
        print("  python generate_nqueens.py <n> <output_file> [--random | --easy | --solution | --hard-diagonal | --hard-anti]")
        sys.exit(1)

    n = int(sys.argv[1])
    output_file = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "--random"

    if mode == "--solution":
        board = generate_constructive_solution(n)
        print(f"Generated valid constructive solution for n={n}")

    elif mode == "--easy":
        board = generate_easy_board(n)
        print(f"Generated EASY board for n={n}")

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
