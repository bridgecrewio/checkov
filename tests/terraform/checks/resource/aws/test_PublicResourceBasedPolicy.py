import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.PublicResourceBasedPolicy import check
from checkov.terraform.runner import Runner


class TestIAMPublicActionsPolicy(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_PublicResourceBasedPolicy"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_sqs_queue_policy.pass1",
            "aws_sqs_queue_policy.pass2",
            "aws_sqs_queue_policy.pass3",
            "aws_sqs_queue_policy.pass4",
            "aws_sns_topic_policy.pass1",
            "aws_sns_topic_policy.pass2",
            "aws_sns_topic_policy.pass3",
            "aws_sns_topic_policy.pass4",
            "aws_s3_bucket_policy.pass1",
            "aws_s3_bucket_policy.pass2",
            "aws_s3_bucket_policy.pass3",
            "aws_s3_bucket_policy.pass4"
        }
        failing_resources = {
            "aws_sqs_queue_policy.fail",
            "aws_sqs_queue_policy.fail2",
            "aws_sns_topic_policy.fail",
            "aws_sns_topic_policy.fail2",
            "aws_s3_bucket_policy.fail",
            "aws_s3_bucket_policy.fail2"
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
