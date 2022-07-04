import os
import unittest

from checkov.gitlab_ci.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        checks = ["CKV_GITLABCI_1","CKV_GITLABCI_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework='github_ci', checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 5)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()


if __name__ == "__main__":
    unittest.main()
