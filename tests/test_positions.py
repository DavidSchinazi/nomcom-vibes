#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bin')))

import bin.positions as positions


class TestGetNomcomId(unittest.TestCase):
    def setUp(self):
        self.orig_cwd = os.getcwd()
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        positions.NOMCOM_ID = None
        positions.NOMCOM_YEAR = None

    def tearDown(self):
        os.chdir(self.orig_cwd)
        self.temp_dir.cleanup()
        positions.NOMCOM_ID = None
        positions.NOMCOM_YEAR = None

    @patch('bin.positions.requests.get')
    @patch('builtins.input', return_value='2026')
    def test_first_run_queries_api_and_saves_file(self, mock_input, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "objects": [
                {"id": 15, "public_key": None},
                {"id": 16, "public_key": "https://www.ietf.org/lib/dt/media/nomcom2025/public_bwBQbeq.cert"},
                {"id": 17, "public_key": "https://www.ietf.org/lib/dt/media/nomcom2026/public_xyz123.cert"},
            ]
        }
        mock_get.return_value = mock_response

        nomcom_id = positions.get_nomcom_id()

        self.assertEqual(nomcom_id, 17)
        mock_input.assert_called_once()
        mock_get.assert_called_once_with("https://datatracker.ietf.org/api/v1/nomcom/nomcom/?limit=1000")
        self.assertTrue(os.path.exists("config/nomcom_id.txt"))
        with open("config/nomcom_id.txt", "r", encoding="utf-8") as f:
            self.assertEqual(f.read().strip(), "17")
        self.assertTrue(os.path.exists("config/nomcom_year.txt"))
        with open("config/nomcom_year.txt", "r", encoding="utf-8") as f:
            self.assertEqual(f.read().strip(), "2026")

    @patch('bin.positions.requests.get')
    @patch('builtins.input')
    def test_subsequent_run_reads_from_disk(self, mock_input, mock_get):
        os.makedirs("config", exist_ok=True)
        with open("config/nomcom_id.txt", "w", encoding="utf-8") as f:
            f.write("17\n")

        nomcom_id = positions.get_nomcom_id()

        self.assertEqual(nomcom_id, 17)
        mock_input.assert_not_called()
        mock_get.assert_not_called()

    @patch('bin.positions.requests.get')
    @patch('builtins.input', return_value='2099')
    def test_missing_year_raises_and_does_not_save(self, mock_input, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "objects": [
                {"id": 16, "public_key": "https://www.ietf.org/lib/dt/media/nomcom2025/public_bwBQbeq.cert"},
            ]
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            positions.get_nomcom_id()

        self.assertFalse(os.path.exists("config/nomcom_id.txt"))


class TestPositionNames(unittest.TestCase):
    def test_2026_position_short_and_full_names(self):
        expected_mappings = {
            "The Web and Internet Transport (WIT) AD": "WIT",
            "Security Area (SEC) AD": "SEC",
            "Routing Area (RTG) AD": "RTG",
            "Operations and Management Area (OPS) AD": "OPS",
            "Internet Area (INT) AD": "INT",
            "Applications and Real-Time Area (ART) AD": "ART",
            "Internet Architecture Board (IAB), Member": "IAB",
            "IETF IPMC Board, Director": "IPMC",
        }
        for full_name, expected_short in expected_mappings.items():
            short = positions.get_position_short_name(full_name)
            self.assertEqual(short, expected_short, f"Failed for {full_name}")
            derived_full = positions.get_position_full_name(short)
            self.assertIsNotNone(derived_full)
            self.assertNotEqual(derived_full, "None")

    def test_unknown_position_name_does_not_return_none(self):
        unknown = "Custom Novel Working Group Chair"
        self.assertEqual(positions.get_position_short_name(unknown), unknown)
        self.assertEqual(positions.get_position_full_name(unknown), unknown)
        self.assertIsNotNone(positions.get_position_full_name("NONEXISTENT"))


class TestFeedbackHelpers(unittest.TestCase):
    def test_clean_session_id(self):
        import bin.feedback as feedback
        self.assertEqual(feedback.clean_session_id("sessionid=abc123xyz;"), "abc123xyz")
        self.assertEqual(feedback.clean_session_id("  sessionid=abc123xyz; \n"), "abc123xyz")
        self.assertEqual(feedback.clean_session_id("abc123xyz"), "abc123xyz")
        self.assertEqual(feedback.clean_session_id('"abc123xyz"'), "abc123xyz")

    def test_is_sign_in_page(self):
        import bin.feedback as feedback
        login_html = "<html><head><title>Sign in</title></head><body>Please sign in</body></html>"
        feedback_html = "<html><head><title>Feedback</title></head><body><div id='comment'>Nice</div></body></html>"
        self.assertTrue(feedback.is_sign_in_page(login_html))
        self.assertFalse(feedback.is_sign_in_page(feedback_html))


if __name__ == '__main__':
    unittest.main()
