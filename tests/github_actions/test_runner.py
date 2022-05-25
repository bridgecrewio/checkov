import os
import unittest

from checkov.github_actions.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", ".github", "workflows")
        runner = Runner()
        checks = ["CKV_GHA_1", "CKV_GHA_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework='github_actions', checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 7)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 35)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()


if __name__ == "__main__":
    unittest.main()
