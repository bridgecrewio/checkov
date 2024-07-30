import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.S3AllowsAnyPrincipal import check
from checkov.terraform.runner import Runner


class TestS3AllowsAnyPrincipal(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_S3AllowsAnyPrincipal"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_s3_bucket.pass",
            "aws_s3_bucket.pass2",
            "aws_s3_bucket_policy.pass",
            "aws_s3_bucket_policy.pass_w_condition",
            "aws_s3_bucket.pass_w_condition",
            "aws_s3_bucket_policy.pass_w_condition2",
            "aws_s3_bucket.pass_w_condition2",
            "aws_s3_bucket.pass_w_condition3",
            "aws_s3_bucket.pass_w_condition4",
            "aws_s3_bucket.pass_w_condition5",
            "aws_s3_bucket.pass_w_condition6",
        }
        failing_resources = {
            "aws_s3_bucket.fail",
            "aws_s3_bucket.fail2",
            "aws_s3_bucket.fail3",
            "aws_s3_bucket_policy.fail",
            "aws_s3_bucket.fail_w_condition",
            "aws_s3_bucket_policy.fail_w_condition",
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
