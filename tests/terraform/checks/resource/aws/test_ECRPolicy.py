import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ECRPolicy import check
from checkov.terraform.runner import Runner


class TestECRPolicy(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_ECRPolicy"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_ecr_repository_policy.pass",
            "aws_ecr_repository_policy.empty",
            "aws_ecr_repository_policy.pass_conditional",
            "aws_ecr_repository_policy.cond_any_pass",
            "aws_ecr_repository_policy.cond_equals_pass",
            "aws_ecr_repository_policy.pass_without_principal"
        }
        failing_resources = {
            "aws_ecr_repository_policy.fail",
            "aws_ecr_repository_policy.fail_conditional",
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