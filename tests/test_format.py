#!/usr/bin/env python3

import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin')))
from bin.format import run_formatting
class TestFormat(unittest.TestCase):

    def test_run_formatting(self):
        # This is a basic test to ensure the script runs without errors.
        # It doesn't check the output, but it will fail if the script crashes.
        run_formatting()

if __name__ == '__main__':
    unittest.main()
