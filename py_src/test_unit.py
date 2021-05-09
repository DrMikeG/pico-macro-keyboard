import unittest
import os

from main import countCycles

class TestStringMethods(unittest.TestCase):

    def test_main_countCycles(self):
        cycles = countCycles()
        self.assertEqual(cycles,10)

if __name__ == '__main__':
    unittest.main()