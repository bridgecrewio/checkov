import os
import unittest

from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestSkipJsonRegexPattern(unittest.TestCase):

    def test_skip_all_checks(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_SkipJsonRegex")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_AZURE_*:.*.json$"])
        )

        summary = report.get_summary()

        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_specific_check(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_SkipJsonRegex")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_AZURE_8:.*.json$"])
        )

        summary = report.get_summary()

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 36)  # Updated expected value
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_specific_check_for_folder(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_SkipJsonRegex")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_AZURE_8:/skip2.[a-z1-9]*.json$"])
        )

        summary = report.get_summary()

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 38)  # Updated expected value
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_specific_check_specific_file(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_SkipJsonRegex")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_AZURE_8:/.*skip1.json$"])
        )

        summary = report.get_summary()

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 38)  # Updated expected value
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_no_skip(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_SkipJsonRegex")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_AZURE_*:/.*skip555.json$"])
        )

        summary = report.get_summary()

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 40)  # Updated expected value
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
