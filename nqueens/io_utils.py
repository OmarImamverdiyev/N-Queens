"""
Input/output helpers for N-Queens files.

@Authors: Omar Imamverdiyev, Mehriban Aliyeva
"""


def read_input(filename):
    """
    Read one integer column index per line into a board list.

    Lines may include comments starting with '#'. Blank lines are ignored.
    """
    with open(filename, "r", encoding="utf-8") as f:
        board: list[int] = []
        for raw_line in f:
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            board.append(int(line))

    n = len(board)
    if n == 0:
        raise ValueError("Input file does not contain any queen positions.")

    for row, col in enumerate(board):
        if col < 0 or col >= n:
            raise ValueError(
                f"Invalid column at row {row}: {col}. Expected 0 <= column < {n}."
            )

    if len(set(board)) != n:
        raise ValueError(
            "Input board must place exactly one queen in each column "
            "(column values must be a permutation of 0..n-1)."
        )

    return board
