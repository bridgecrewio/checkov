import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.IAMStarResourcePolicyDocument import check
from checkov.terraform.checks.utils.base_cloudsplaining_iam_scanner import BaseTerraformCloudsplainingIAMScanner
from checkov.terraform.runner import Runner


class TestIAMStarResourcePolicyDocument(unittest.TestCase):
    def setUp(self) -> None:
        # make sure nothing is in the cache
        BaseTerraformCloudsplainingIAMScanner.policy_document_cache = {}

    def tearDown(self) -> None:
        BaseTerraformCloudsplainingIAMScanner.policy_document_cache = {}

    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_IAMStarResourcePolicyDocument"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_iam_policy.pass",
            "aws_iam_policy.pass_unrestrictable",
            "aws_iam_role_policy.pass",
            "aws_iam_user_policy.pass",
            "aws_iam_group_policy.pass",
            "aws_ssoadmin_permission_set_inline_policy.pass"
        }
        failing_resources = {
            "aws_iam_policy.fail",
            "aws_iam_role_policy.fail",
            "aws_iam_user_policy.fail",
            "aws_iam_group_policy.fail",
            "aws_ssoadmin_permission_set_inline_policy.fail"
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

