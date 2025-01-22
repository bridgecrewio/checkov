import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.data.aws.GithubActionsOIDCTrustPolicy import check
from checkov.terraform.runner import Runner
from checkov.terraform.plan_runner import Runner as PlanRunner


class TestGithubActionsOIDCTrustPolicy(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_GithubActionsOIDCTrustPolicy"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'aws_iam_policy_document.pass1',
            "aws_iam_policy_document.pass2",
            "aws_iam_policy_document.pass3",
            "aws_iam_policy_document.pass-org-only"
        }
        failing_resources = {
            "aws_iam_policy_document.fail1",
            "aws_iam_policy_document.fail2",
            "aws_iam_policy_document.fail-wildcard",
            "aws_iam_policy_document.fail-abusable",
            "aws_iam_policy_document.fail-wildcard-assertion",
            "aws_iam_policy_document.fail-misused-repo"
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_terraform_plan(self):
        runner = PlanRunner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_path = current_dir + "/example_GithubActionsOIDCTrustPolicy/tfplan.json"
        report = runner.run(files=[test_files_path], runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'module.poc.data.aws_iam_policy_document.r4["p1"]',
            'module.poc.data.aws_iam_policy_document.r4["p2"]',
            'module.poc.data.aws_iam_policy_document.r3["p1"]',
            'module.poc.data.aws_iam_policy_document.r3["p2"]',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)


if __name__ == "__main__":
    unittest.main()
