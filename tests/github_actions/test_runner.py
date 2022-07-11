import unittest
from pathlib import Path

from checkov.github_actions.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):
    def test_runner(self):
        # given
        test_dir = Path(__file__).parent / "resources"
        checks = ["CKV_GHA_1", "CKV_GHA_2"]

        # when
        report = Runner().run(
            root_folder=str(test_dir), runner_filter=RunnerFilter(framework=["github_actions"], checks=checks)
        )

        # then
        self.assertEqual(len(report.failed_checks), 7)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 35)
        self.assertEqual(len(report.skipped_checks), 0)


if __name__ == "__main__":
    unittest.main()
