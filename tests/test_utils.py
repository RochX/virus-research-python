import unittest

import sympy as sp

from utils.generatinglist_utils import has_same_number_elements
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
