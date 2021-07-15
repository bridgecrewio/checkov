import unittest

import os
from pathlib import Path

from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_tf_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform_failed"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(2, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_tf_skip_check(self):
        valid_dir_path = Path(__file__).parent / "resources/terraform_skip"

        report = Runner().run(
            root_folder=valid_dir_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework='secrets')
        )

        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

        report.print_console()

    def test_runner_skip_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets', skip_checks=['CKV_SECRET_2']))
        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_multiple_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='secrets'))
        self.assertEqual(5, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

if __name__ == '__main__':
    unittest.main()
