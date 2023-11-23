from unittest import TestCase
import pickle_loader_saver
from pickle_loader_saver import has_same_number_elements


class Test(TestCase):
    def test_has_same_number_elements(self):
        self.assertTrue(has_same_number_elements(1, 2))
        self.assertTrue(has_same_number_elements((1,), (2,)))
        self.assertTrue(has_same_number_elements((1, 1), (2, 2)))
        self.assertFalse(has_same_number_elements((3, 3), (4, 4, 4)))
        self.assertFalse(has_same_number_elements(5, (6, 6)))
        self.assertFalse(has_same_number_elements(10, {}))
        self.assertTrue(has_same_number_elements({}, {}))
        self.assertFalse(has_same_number_elements({1: 2}, {}))
