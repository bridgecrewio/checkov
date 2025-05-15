import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SNSCrossAccountAccess import check
from checkov.terraform.runner import Runner


class TestSNSOverPermissivePublishing(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_SNSCrossAccountAccess"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_sns_topic_policy.pass0",
            "aws_sns_topic_policy.pass1",
            "aws_sns_topic_policy.pass2",
        }
        failing_resources = {
            "aws_sns_topic_policy.fail0",
            "aws_sns_topic_policy.fail1",
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
