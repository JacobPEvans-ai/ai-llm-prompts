import unittest

from src.average import average


class AverageTests(unittest.TestCase):
    def test_average_uses_the_defined_count(self):
        self.assertEqual(average([2, 4]), 3)
