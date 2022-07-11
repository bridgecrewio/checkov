import os
import unittest

from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter

class TestRunnerValid(unittest.TestCase):

    def test_runner(self) -> None:
        current_dir = os.path.dirname(__file__)
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        checks = ["CKV_OPENAPI_1", "CKV_OPENAPI_4", "CKV_OPENAPI_3"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework='openapi', checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 12)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 6)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()


    def test_runner_all_checks(self) -> None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework='openapi')
        )
        report.print_console()


if __name__ == "__main__":
    unittest.main()