import unittest

import os

from checkov.json_doc.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def test_runner_object_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "object", "fail")
        checks_dir = os.path.join(current_dir, "checks", "object")
        runner = Runner()
        checks = ["CKV_FOO_1", "CKV_FOO_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework='all', checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_object_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "object", "pass")
        checks_dir = os.path.join(current_dir, "checks", "object")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_FOO_1"]),
        )
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_array_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "array", "fail")
        checks_dir = os.path.join(current_dir, "checks", "array")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework='all', checks=["CKV_BARBAZ_1"])
        )
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_array_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "array", "pass")
        checks_dir = os.path.join(current_dir, "checks", "array")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_BARBAZ_1"]),
        )
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_complex_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "complex", "fail")
        checks_dir = os.path.join(current_dir, "checks", "complex")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework='all', checks=["CKV_COMPLEX_1"])
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_complex_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "complex", "pass")
        checks_dir = os.path.join(current_dir, "checks", "complex")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            external_checks_dir=[checks_dir],
            runner_filter=RunnerFilter(framework="all", checks=["CKV_COMPLEX_1"]),
        )
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()


if __name__ == "__main__":
    unittest.main()
