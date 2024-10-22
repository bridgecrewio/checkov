import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.S3AbortIncompleteUploads import check
from checkov.terraform.runner import Runner


class TestS3AbortIncompleteUploads(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_S3AbortIncompleteUploads"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_s3_bucket_lifecycle_configuration.pass",
            "aws_s3_bucket_lifecycle_configuration.pass2",
            "aws_s3_bucket_lifecycle_configuration.pass3",
            "aws_s3_bucket_lifecycle_configuration.resource_with_dynamic_rule_pass4"
        }
        failing_resources = {
            "aws_s3_bucket_lifecycle_configuration.fail",
            "aws_s3_bucket_lifecycle_configuration.fail2",
            "aws_s3_bucket_lifecycle_configuration.fail3",
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
