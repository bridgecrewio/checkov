import time
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.secrets.plugins.entropy_keyword_combinator import EntropyKeywordCombinator
from checkov.secrets.runner import Runner


class TestCombinatorPluginMultilineJson(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = EntropyKeywordCombinator()

    def test_multiline_keyword_password_report(self):
        test_file_path = Path(__file__).parent / "json_multiline/test-multiline-secrets.json"

        report = Runner().run(
            root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=['secrets'])
        )
        self.assertEqual(len(report.failed_checks), 5)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_non_multiline_pair_time_limit_creating_report(self):
        # given
        test_files = [str(Path(__file__).parent / "json_multiline/pomerium_compose.json")]
        runner = Runner()
        runner_filter = RunnerFilter(framework=['secrets'])

        # when
        start_time = time.time()
        report = runner.run(root_folder=None, files=test_files, runner_filter=runner_filter)
        end_time = time.time()

        # then
        assert end_time-start_time < 1  # assert the time limit is not too long for parsing long lines.
        self.assertEqual(len(report.failed_checks), 6)
        # None of the results is related to multiline scanning - all is detected even if multiline scanning is disabled.
        # This is a different result compared to same data in .yml file.
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
