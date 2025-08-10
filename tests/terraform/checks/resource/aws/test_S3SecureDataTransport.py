import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.S3SecureDataTransport import check
from checkov.terraform.runner import Runner


class TestS3SecureDataTransport(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_S3SecureDataTransport"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_s3_bucket_acl.pass_private",
            "aws_s3_bucket_acl.pass_restricted",
            "aws_s3_bucket_acl.pass_grant_blocked",
            "aws_s3_bucket_acl.pass_website",
            "aws_s3_bucket_acl.pass_policy1",
            "aws_s3_bucket_acl.pass_policy2",
            "aws_s3_bucket_acl.pass_policy3",
        }
        failing_resources = {
            "aws_s3_bucket_acl.fail1",
            "aws_s3_bucket_acl.fail2",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 7)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
