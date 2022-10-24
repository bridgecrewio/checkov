import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SQSQueuePolicyAnyPrincipal import check
from checkov.terraform.runner import Runner


class TestBackupVaultEncrypted(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SQSQueuePolicyAnyPrincipal"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_sqs_queue_policy.q1",
            "aws_sqs_queue_policy.q6",
            "aws_sqs_queue.aq1",
            "aws_sqs_queue.aq6"
        }
        failing_resources = {
            "aws_sqs_queue_policy.q2",
            "aws_sqs_queue_policy.q3",
            "aws_sqs_queue_policy.q4",
            "aws_sqs_queue_policy.q5",
            "aws_sqs_queue.aq2",
            "aws_sqs_queue.aq3",
            "aws_sqs_queue.aq4",
            "aws_sqs_queue.aq5",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 8)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()