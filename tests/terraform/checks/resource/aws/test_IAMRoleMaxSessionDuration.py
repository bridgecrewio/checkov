import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.IAMRoleMaxSessionDuration import check
from checkov.terraform.runner import Runner


class TestIAMRoleMaxSessionDuration(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_IAMRoleMaxSessionDuration"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_iam_role.pass",
            "aws_iam_role.pass_explicit",
        }
        failing_resources = {
            "aws_iam_role.fail",
            "aws_iam_role.fail_boundary",
        }
        # variable-dependent max_session_duration is UNKNOWN and should not be pass/fail
        unknown_resources = {
            "aws_iam_role.unknown",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)
        self.assertEqual(len([r for r in report.resources if r in unknown_resources]), 0)


if __name__ == "__main__":
    unittest.main()
