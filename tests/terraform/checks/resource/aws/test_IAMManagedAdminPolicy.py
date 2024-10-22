import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.aws.IAMManagedAdminPolicy import check


class TestIAMManagedAdminPolicy(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_IAMManagedAdminPolicy")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_iam_role.pass1",
            "aws_iam_policy_attachment.pass2",
            "aws_iam_role_policy_attachment.pass3",
            "aws_iam_user_policy_attachment.pass4",
            "aws_iam_group_policy_attachment.pass5",
            "aws_iam_role_policy_attachment.pass6",
            "aws_ssoadmin_managed_policy_attachment.pass7",
        }

        failing_resources = {
            "aws_iam_role.fail1",
            "aws_iam_policy_attachment.fail2",
            "aws_iam_role_policy_attachment.fail3",
            "aws_iam_user_policy_attachment.fail4",
            "aws_iam_group_policy_attachment.fail5",
            "aws_ssoadmin_managed_policy_attachment.fail6",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()