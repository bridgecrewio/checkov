import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.S3ProtectAgainstPolicyLockout import check
from checkov.terraform.runner import Runner


class TestS3ProtectAgainstPolicyLockout(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_S3ProtectAgainstPolicyLockout"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_s3_bucket_policy.pass",
            "aws_s3_bucket_policy.pass2",
            "aws_s3_bucket_policy.pass3",
            "aws_s3_bucket_policy.pass4",
            "aws_s3_bucket_policy.pass5",
            "aws_s3_bucket_policy.baddata"

        }
        failing_resources = {
            "aws_s3_bucket_policy.failjsonencode",
            "aws_s3_bucket_policy.multi_statement_fail",
            "aws_s3_bucket_policy.fail",
            "aws_s3_bucket.deprecated",
            "aws_s3_bucket.deprecated2"
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
