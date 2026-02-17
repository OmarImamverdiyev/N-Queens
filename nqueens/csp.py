# csp.py
import random


class NQueensCSP:
    def __init__(self, n, initial_board=None):
        self.n = n

        if initial_board:
            self.board = initial_board.copy()
        else:
            self.board = [random.randint(0, n - 1) for _ in range(n)]

        self.col_count = [0] * n
        self.diag1_count = [0] * (2 * n)
        self.diag2_count = [0] * (2 * n)

        self._build_counters()

    def _build_counters(self):
        for row in range(self.n):
            col = self.board[row]
            self.col_count[col] += 1
            self.diag1_count[row - col + self.n] += 1
            self.diag2_count[row + col] += 1

    def conflicts(self, row, col):
        return (
            self.col_count[col]
            + self.diag1_count[row - col + self.n]
            + self.diag2_count[row + col]
            - 3 * (self.board[row] == col)
        )

    def solve(self, max_steps=100000):
        for _ in range(max_steps):

            conflicted_rows = [
                row for row in range(self.n)
                if self.conflicts(row, self.board[row]) > 0
            ]

            if not conflicted_rows:
                return True

            row = random.choice(conflicted_rows)

            min_conf = float("inf")
            best_cols = []

            for col in range(self.n):
                c = self.conflicts(row, col)
                if c < min_conf:
                    min_conf = c
                    best_cols = [col]
                elif c == min_conf:
                    best_cols.append(col)

            new_col = random.choice(best_cols)
            self._move_queen(row, new_col)

        return False

    def _move_queen(self, row, new_col):
        old_col = self.board[row]

        self.col_count[old_col] -= 1
        self.diag1_count[row - old_col + self.n] -= 1
        self.diag2_count[row + old_col] -= 1

        self.board[row] = new_col

        self.col_count[new_col] += 1
        self.diag1_count[row - new_col + self.n] += 1
        self.diag2_count[row + new_col] += 1
