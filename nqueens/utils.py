"""General utility helpers for N-Queens."""


def is_valid(board):
    """Return True if no two queens attack each other."""
    n = len(board)
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j]:
                return False
            if abs(board[i] - board[j]) == abs(i - j):
                return False
    return True
