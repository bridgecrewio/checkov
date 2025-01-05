import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.terraform.terraform.StateLock import check
from checkov.terraform.runner import Runner
from checkov.terraform_json.runner import TerraformJsonRunner


class TestStateLock(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/resources/lock"
        report = runner.run(
            root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id])
        )
        summary = report.get_summary()

        # using file paths, because the resources have all the same name
        passing_file_paths = {
            "pass.tf",
            "pass_dynamodb_table.tf",
        }
        failing_file_paths = {
            "fail1.tf",
        }

        passed_check_file_paths = {Path(c.file_path).name for c in report.passed_checks}
        failed_check_file_paths = {Path(c.file_path).name for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_file_paths, passed_check_file_paths)
        self.assertEqual(failing_file_paths, failed_check_file_paths)

    def test_tf_json(self):
        runner = TerraformJsonRunner()

        test_files_dir = Path(__file__).parent / "resources/lock"
        report = runner.run(
            root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id])
        )
        summary = report.get_summary()

        # using file paths, because the resources have all the same name
        passing_file_paths = {
            "pass.cdk.tf.json",
        }
        failing_file_paths = {
            "fail.cdk.tf.json",
        }

        passed_check_file_paths = {Path(c.file_path).name for c in report.passed_checks}
        failed_check_file_paths = {Path(c.file_path).name for c in report.failed_checks}

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_file_paths, passed_check_file_paths)
        self.assertEqual(failing_file_paths, failed_check_file_paths)


if __name__ == '__main__':
    unittest.main()
