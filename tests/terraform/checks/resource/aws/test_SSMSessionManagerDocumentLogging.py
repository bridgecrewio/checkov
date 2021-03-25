import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SSMSessionManagerDocumentLogging import check
from checkov.terraform.runner import Runner


class TestSSMSessionManagerDocumentLogging(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SSMSessionManagerDocumentLogging"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_ssm_document.s3_enabled_encrypted",
            "aws_ssm_document.s3_enabled_encrypted_yaml",
            "aws_ssm_document.cw_enabled_encrypted",
            "aws_ssm_document.cw_enabled_encrypted_yaml",
        }
        failing_resources = {
            "aws_ssm_document.disabled",
            "aws_ssm_document.disabled_yaml",
            "aws_ssm_document.s3_enabled_not_encrypted",
            "aws_ssm_document.s3_enabled_not_encrypted_yaml",
            "aws_ssm_document.cw_enabled_not_encrypted",
            "aws_ssm_document.cw_enabled_not_encrypted_yaml",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 6)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
