import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SNSTopicPolicyAnyPrincipal import check
from checkov.terraform.runner import Runner


class TestBackupVaultEncrypted(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SNSTopicPolicyAnyPrincipal"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_sns_topic_policy.sns_tp1",
            "aws_sns_topic_policy.sns_tp6",
            "aws_sns_topic_policy.sns_pass_condition",
        }
        failing_resources = {
            "aws_sns_topic_policy.sns_tp2",
            "aws_sns_topic_policy.sns_tp3",
            "aws_sns_topic_policy.sns_tp4",
            "aws_sns_topic_policy.sns_tp5",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()