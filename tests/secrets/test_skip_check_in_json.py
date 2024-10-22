import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner


class TestCustomRegexDetector(unittest.TestCase):

    def test_no_skip(self) -> None:
        """
        Pass regex pattern which is not apply on any file from test_files_dir
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1/skip_test2")

        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*3.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 10)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_on_one1(self) -> None:
        """
        Pass regex pattern which is apply on one file - first check
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1/skip_test2")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*1.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 5)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_on_one2(self) -> None:
        """
        Pass regex pattern which is apply on one file - second check
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1/skip_test2")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*2.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 5)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_both(self) -> None:
        """
        Pass regex pattern apply all files in root folder
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1/skip_test2")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 10)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_directory_pattern(self) -> None:
        """
        Pass regex pattern which is only apply on one directory pattern
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*skip_test2.*json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 10)
        self.assertEqual(summary['skipped'], 10)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_file_pattern(self) -> None:
        """
        Pass regex pattern which is only apply on certain file pattern
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*skip1.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 10)
        self.assertEqual(summary['skipped'], 10)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_invalid_regex(self) -> None:
        """
        Pass invalid regex pattern
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:[a-z]++$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 20)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_one_good_one_invalid_regex(self) -> None:
        """
        Pass both good & invalid regex pattern
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:[a-z]++$", "CKV_SECRET_6:.*skip1.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 10)
        self.assertEqual(summary['skipped'], 10)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_two_files_regex_patterns(self) -> None:
        """
        Pass two different regex patterns (file patterns)
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test/skip_test1")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*skip2.json$", "CKV_SECRET_6:.*skip1.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 20)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_two_dir_regex_patterns(self) -> None:
        """
        Pass two different regex patterns (directory related)
        """
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "skip_test")
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV_SECRET_6:.*skip1.*.json$", "CKV_SECRET_6:.*skip2.*.json$"]))

        summary = report.get_summary()
        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 30)
        self.assertEqual(summary['parsing_errors'], 0)
