import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.EBSDefaultEncryption import check
from checkov.terraform.runner import Runner


class TestEBSDefaultEncryption(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_EBSDefaultEncryption"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_ebs_encryption_by_default.enabled",
            "aws_ebs_encryption_by_default.default",
            "aws_ebs_encryption_by_default.null",
        }
        failing_resources = {
            "aws_ebs_encryption_by_default.disabled",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
