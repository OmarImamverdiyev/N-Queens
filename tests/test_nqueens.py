import os
import tempfile
import unittest
from unittest.mock import patch

from nqueens.ac3 import ac3, queens_compatible, revise
from nqueens.csp import NQueensCSP
from nqueens.csp_state import NQueensState
from nqueens.io_utils import read_input
from nqueens.utils import is_valid


class TestIOUtils(unittest.TestCase):
    def _write_temp(self, content: str) -> str:
        fd, path = tempfile.mkstemp(text=True)
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_read_input_supports_comments_and_blanks(self) -> None:
        path = self._write_temp("""
            # sample board
            1

            3   # row 1
            0
            2
        """)
        try:
            board = read_input(path)
            self.assertEqual(board, [1, 3, 0, 2])
        finally:
            os.remove(path)

    def test_read_input_rejects_duplicate_columns(self) -> None:
        path = self._write_temp("0\n1\n1\n3\n")
        try:
            with self.assertRaises(ValueError):
                read_input(path)
        finally:
            os.remove(path)

    def test_read_input_rejects_out_of_range_column(self) -> None:
        path = self._write_temp("0\n1\n4\n3\n")
        try:
            with self.assertRaises(ValueError):
                read_input(path)
        finally:
            os.remove(path)


class TestAC3(unittest.TestCase):
    def test_queens_compatible(self) -> None:
        self.assertFalse(queens_compatible(0, 0, 1, 0))
        self.assertFalse(queens_compatible(0, 0, 1, 1))
        self.assertTrue(queens_compatible(0, 1, 1, 3))

    def test_revise_removes_unsupported_values(self) -> None:
        domains = [{0, 1, 2}, {0}]
        changed = revise(domains, 0, 1)
        self.assertTrue(changed)
        self.assertEqual(domains[0], {2})

    def test_ac3_detects_inconsistency(self) -> None:
        domains = [{0, 1}, {0, 1}]
        self.assertFalse(ac3(domains))


class TestStateAndCSP(unittest.TestCase):
    def test_state_move_queen_updates_counts(self) -> None:
        state = NQueensState(n=4, board=[1, 3, 0, 2])
        state.move_queen(0, 2)

        expected_cols = [0] * state.n
        expected_diag1 = [0] * (2 * state.n)
        expected_diag2 = [0] * (2 * state.n)
        for row, col in enumerate(state.board):
            expected_cols[col] += 1
            expected_diag1[row - col + state.n] += 1
            expected_diag2[row + col] += 1

        self.assertEqual(state.col_count, expected_cols)
        self.assertEqual(state.diag1_count, expected_diag1)
        self.assertEqual(state.diag2_count, expected_diag2)

    def test_is_valid(self) -> None:
        self.assertTrue(is_valid([1, 3, 0, 2]))
        self.assertFalse(is_valid([0, 1, 2, 3]))

    def test_csp_solve_resets_to_random_permutation(self) -> None:
        solver = NQueensCSP(n=10, initial_board=[0] * 10)

        with patch("nqueens.csp.solve_min_conflicts", return_value=True) as mocked:
            ok = solver.solve(max_steps=5)

        self.assertTrue(ok)
        self.assertTrue(mocked.called)

        self.assertEqual(len(solver.board), 10)
        self.assertEqual(set(solver.board), set(range(10)))
        self.assertNotEqual(solver.board, [0] * 10)

    def test_csp_solve_uses_input_board_when_requested(self) -> None:
        initial_board = [1, 3, 5, 7, 9, 0, 2, 4, 6, 8]
        solver = NQueensCSP(n=10, initial_board=initial_board, start_mode="input")

        with patch("nqueens.csp.solve_min_conflicts", return_value=True) as mocked:
            ok = solver.solve(max_steps=5)

        self.assertTrue(ok)
        self.assertTrue(mocked.called)
        self.assertEqual(solver.board, initial_board)


if __name__ == "__main__":
    unittest.main()
