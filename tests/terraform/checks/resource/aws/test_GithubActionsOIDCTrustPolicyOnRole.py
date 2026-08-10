import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.GithubActionsOIDCTrustPolicyOnRole import check
from checkov.terraform.runner import Runner


class TestGithubActionsOIDCTrustPolicyOnRole(unittest.TestCase):
    """
    Resource-level mirror of CKV_AWS_358 (data-source-only).

    This test asserts behavioral parity with
    tests/terraform/checks/data/aws/test_GithubActionsOIDCTrustPolicy.py
    when the same trust policy is expressed as an inline
    `aws_iam_role.assume_role_policy = jsonencode({...})` instead of a
    `data "aws_iam_policy_document"` block.

    Extra fixture `pass-fm-customer` locks in the XSUP-69131 regression
    marker: Freddie Mac's `repo:freddiemac/*` value is intentionally
    treated as PASSED, matching CKV_AWS_358's `pass-org-only` semantics.
    """

    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_GithubActionsOIDCTrustPolicyOnRole"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_iam_role.pass1",
            "aws_iam_role.pass2",
            "aws_iam_role.pass3",
            "aws_iam_role.pass_aud_first",
            "aws_iam_role.pass-org-only",
            "aws_iam_role.pass-gh-org",
            "aws_iam_role.pass-fm-customer",
        }
        failing_resources = {
            "aws_iam_role.fail1",
            "aws_iam_role.fail2",
            "aws_iam_role.fail-wildcard",
            "aws_iam_role.fail-abusable",
            "aws_iam_role.fail-wildcard-assertion",
            "aws_iam_role.fail-misused-repo",
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
