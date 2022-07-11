import os
import unittest

from checkov.circleci_pipelines.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        checks = []
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework=['circleci_pipelines'], checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 19)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 19)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()


if __name__ == "__main__":
    unittest.main()
