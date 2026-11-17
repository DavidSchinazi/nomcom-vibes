#!/usr/bin/env python3

import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin')))
from bin.format import run_formatting, get_source_logo_path, copy_logo
from unittest.mock import patch

class TestFormat(unittest.TestCase):

    def test_run_formatting(self):
        # This is a basic test to ensure the script runs without errors.
        # It doesn't check the output, but it will fail if the script crashes.
        run_formatting(summaries_forced=False)

    @patch('bin.format.get_nomcom_year', return_value='2026')
    @patch('bin.format.os.path.exists')
    def test_get_source_logo_path_2026_with_file(self, mock_exists, mock_year):
        mock_exists.side_effect = lambda path: path == "static/logo-2026.jpg"
        self.assertEqual(get_source_logo_path(), "static/logo-2026.jpg")

    @patch('bin.format.get_nomcom_year', return_value='2026')
    @patch('bin.format.os.path.exists')
    def test_get_source_logo_path_2026_fallback(self, mock_exists, mock_year):
        mock_exists.side_effect = lambda path: path == "static/logo.jpg"
        self.assertEqual(get_source_logo_path(), "static/logo.jpg")

    @patch('bin.format.get_nomcom_year', return_value='2025')
    @patch('bin.format.os.path.exists')
    def test_get_source_logo_path_2025_fallback(self, mock_exists, mock_year):
        mock_exists.side_effect = lambda path: path == "static/logo.jpg"
        self.assertEqual(get_source_logo_path(), "static/logo.jpg")

if __name__ == '__main__':
    unittest.main()
