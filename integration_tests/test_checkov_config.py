import json
import os
import unittest
from unittest import mock
from checkov.common.logger_streams import LoggerStreams
from checkov.logging_init import log_stream, erase_log_stream
from checkov.main import Checkov

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovConfig(unittest.TestCase):
    def test_terragoat_report(self):
        # Report to be generated using following command:
        # checkov -d path/to/terragoat --config-file \
        # path/to/checkov/integration_tests/example_config_files/config.yaml \
        # > path/to/checkov/checkov_config_report_terragoat.json
        report_path = os.path.join(os.path.dirname(current_dir), "checkov_config_report_terragoat.json")
        with open(report_path) as json_file:
            data = json.load(json_file)
            self.assertEqual(
                data["summary"]["parsing_errors"],
                0,
                f"expecting 0 parsing errors but got: {data['results']['parsing_errors']}",
            )
            self.assertGreater(
                data["summary"]["failed"], 1, f"expecting more than 1 failed checks, got: {data['summary']['failed']}"
            )
            self.assertEqual(
                data["check_type"], "terraform", f"expecting 'terraform' but got: {data['check_type']}"
            )
            self.assertIsNotNone(
                data["results"]["failed_checks"][0]["guideline"], "expecting a guideline for checks."
            )

    def setUp(self):
        erase_log_stream()  # Clear any existing logs before each test
        self.logger_streams = LoggerStreams()
        self.stream_name = "test_stream"
        self.logger_streams.add_stream(self.stream_name, log_stream)

    def tearDown(self):
        erase_log_stream()  # Ensure logs are cleared after each test

    def get_logged_messages(self):
        return self.logger_streams.get_streams().get(self.stream_name).getvalue()

    def test_missing_config_file(self):
        """Test when the provided config-file does not exist."""
        config_path = os.path.join('path', 'to', 'missing', 'config.yaml')
        argv = ["--config-file", config_path]

        with mock.patch("pathlib.Path.is_file", return_value=False):
            checkov_instance = Checkov(argv=argv)
            checkov_instance.parse_config()

        logged_messages = self.get_logged_messages()
        expected_message = f"The config file at '{config_path}' does not exist. Running without a config file."
        self.assertIn(expected_message, logged_messages)

    def test_no_config_file_argument(self):
        """Test when no --config-file argument is provided."""
        argv = []

        checkov_instance = Checkov(argv=argv)
        checkov_instance.parse_config()

        logged_messages = self.get_logged_messages()
        self.assertNotIn("does not exist", logged_messages)


if __name__ == "__main__":
    unittest.main()
