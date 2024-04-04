import unittest

import sympy as sp

from utils.generatinglist_utils import has_same_number_elements, is_valid_generating_list
from utils.input_checker import can_be_generating_list, convert_to_generating_list
from utils.sympy_utils import equation_is_true_or_solvable


class GeneratingListUtilTests(unittest.TestCase):
    """Test cases for generatinglist_utils.py."""
    def test_has_same_number_elements(self):
        self.assertTrue(has_same_number_elements(1, 2))
        self.assertTrue(has_same_number_elements((1,), (2,)))
        self.assertTrue(has_same_number_elements((1, 1), (2, 2)))
        self.assertFalse(has_same_number_elements((3, 3), (4, 4, 4)))
        self.assertFalse(has_same_number_elements(5, (6, 6)))
        self.assertFalse(has_same_number_elements(10, {}))
        self.assertTrue(has_same_number_elements({}, {}))
        self.assertFalse(has_same_number_elements({1: 2}, {}))

    def test_is_valid_generating_list(self):
        self.assertTrue(is_valid_generating_list(1))
        self.assertTrue(is_valid_generating_list((1,)))
        self.assertTrue(is_valid_generating_list((1, 2)))
        self.assertFalse(is_valid_generating_list((1, 10)))


class InputCheckerTests(unittest.TestCase):
    """Test cases for input_checker.py."""
    def test_can_be_generating_list(self):
        self.assertTrue(can_be_generating_list(1))
        self.assertTrue(can_be_generating_list((1, 2)))
        self.assertFalse(can_be_generating_list("bad_string_input"))
        self.assertTrue(can_be_generating_list("1"))
        self.assertTrue(can_be_generating_list("(1, 2)"))

    def test_convert_to_generating_list(self):
        self.assertEqual(convert_to_generating_list(1), 1)
        self.assertEqual(convert_to_generating_list((1, 2)), (1, 2))
        self.assertEqual(convert_to_generating_list("3"), 3)
        self.assertEqual(convert_to_generating_list("(4, 5)"), (4, 5))
        with self.assertRaises(ValueError):
            convert_to_generating_list("bad_string_input")


class SympyUtilTests(unittest.TestCase):
    """Test cases for sympy_utils.py."""
    def test_equation_is_true_or_solvable(self):
        ex_eq = sp.Eq(1, 1)
        var_a = sp.Symbol('a', real=True)
        ex_eq_with_var = sp.Eq(1, var_a)

        self.assertTrue(equation_is_true_or_solvable(ex_eq))
        self.assertTrue(equation_is_true_or_solvable(ex_eq_with_var))


if __name__ == '__main__':
    unittest.main()
