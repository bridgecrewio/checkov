import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.WAFACLCVE202144228 import check
from checkov.terraform.runner import Runner


class TestWafHasAnyRules(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_WAFACLCVE202144228"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_wafv2_web_acl.pass",
            "aws_wafv2_web_acl.multi_rules",
            "aws_wafv2_web_acl.pass_dynamic"
        }

        failing_resources = {
            "aws_wafv2_web_acl.no_rule",
            "aws_wafv2_web_acl.wrong_rule",
            "aws_wafv2_web_acl.rule_count",
            "aws_wafv2_web_acl.rule_group_count",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
