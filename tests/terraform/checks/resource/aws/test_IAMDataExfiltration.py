import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.IAMDataExfiltration import check
from checkov.terraform.runner import Runner


class TestIAMDataExfiltration(unittest.TestCase):
    def setUp(self):
        from checkov.terraform.checks.utils.base_cloudsplaining_iam_scanner import BaseTerraformCloudsplainingIAMScanner
        # needs to be reset, because the cache belongs to the class not instance
        BaseTerraformCloudsplainingIAMScanner.policy_document_cache = {}

    def test(self):
        test_files_dir = Path(__file__).parent / "example_IAMDataExfiltration"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_iam_policy.pass",
        }
        failing_resources = {
            "aws_iam_policy.fail",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
