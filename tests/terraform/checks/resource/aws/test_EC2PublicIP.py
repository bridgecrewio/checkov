import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.EC2PublicIP import check
from checkov.terraform.runner import Runner


class TestEC2PublicIP(unittest.TestCase):
    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "True"})
    def test(self):
        test_files_dir = Path(__file__).parent / "example_EC2PublicIP"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_instance.default",
            "aws_instance.private",
            "aws_launch_template.default",
            "aws_launch_template.private",
            "aws_instance.public_foreach[\"key2\"]",
            "aws_instance.public_foreach_loop_list[\"k\"]",
            "aws_instance.public_foreach_loop_list[\"v\"]",
            "aws_instance.public_foreach_loop_list_of_dicts[\"private\"]",
        }
        failing_resources = {
            "aws_instance.public",
            "aws_launch_template.public",
            "aws_instance.public_foreach[\"key1\"]",
            "aws_instance.public_foreach_loop[\"key3\"]",
            "aws_instance.public_foreach_loop[\"key4\"]",
            "aws_instance.public_foreach_loop_list_of_dicts[\"public\"]",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_MODULES_FOREACH_HANDLING": "True"})
    def test_for_each_poc(self):
        test_files_dir = Path(__file__).parent / "example_EC2PublicIP_foreach"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "module.s3_module[\"a\"].aws_instance.poc_modules_foreach[\"key2\"]",
            "module.s3_module[\"b\"].aws_instance.poc_modules_foreach[\"key2\"]",
        }
        failing_resources = {
            "module.s3_module[\"a\"].aws_instance.poc_modules_foreach[\"key1\"]",
            "module.s3_module[\"b\"].aws_instance.poc_modules_foreach[\"key1\"]",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
