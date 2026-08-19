import os
import unittest
from pathlib import Path

import pytest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestCloudfrontDistributionLogging(unittest.TestCase):
    def test_file_v1_and_v2_logging(self):
        test_files_dir = Path(__file__).parent / "example_CloudfrontDistributionLoggingV2"

        report = Runner().run(
            root_folder=str(test_files_dir),
            runner_filter=RunnerFilter(checks=["CKV_AWS_86"]),
        )
        summary = report.get_summary()

        passing_resources = {
            "aws_cloudfront_distribution.pass_v1",
            "aws_cloudfront_distribution.pass_v2",
            "aws_cloudfront_distribution.fail_v2_incomplete_chain",
        }
        failing_resources = {
            "aws_cloudfront_distribution.fail_no_logging",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    @pytest.mark.skip("Need to handle null variables")
    def test_null_var_651(self):
        self.skipTest("Need to handle null variables")
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir,
                                      "../../../parser/resources/parser_scenarios/null_variables_651")
        valid_dir_path = os.path.normpath(valid_dir_path)
        runner = Runner()
        checks_allowlist = ['CKV_AWS_86']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))
        self.assertEqual(len(report.failed_checks), 1)
        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)


if __name__ == '__main__':
    unittest.main()
