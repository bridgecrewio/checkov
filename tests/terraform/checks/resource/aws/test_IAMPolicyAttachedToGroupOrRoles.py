import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.IAMPolicyAttachedToGroupOrRoles import check
from checkov.terraform.runner import Runner


class TestIAMPolicyAttachedToGroupOrRoles(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_IAMPolicyAttachedToGroupOrRoles"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_iam_policy_attachment.pass",
            "aws_iam_policy_attachment.null",
            "aws_iam_policy_attachment.empty",
        }
        failing_resources = {
            "aws_iam_policy_attachment.fail",
            "aws_iam_user_policy.fail",
            "aws_iam_user_policy_attachment.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 3)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
