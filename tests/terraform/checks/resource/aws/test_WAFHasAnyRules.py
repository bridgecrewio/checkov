import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.WAFHasAnyRules import check
from checkov.terraform.runner import Runner


class TestWafHasAnyRules(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_WafHasAnyRules"
        report = runner.run(
            root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id])
        )
        summary = report.get_summary()

        passing_resources = {
            "aws_waf_web_acl.pass",
            'aws_wafv2_web_acl.pass',
            'aws_wafregional_web_acl.pass',
        }

        failing_resources = {
            "aws_waf_web_acl.fail",
            "aws_waf_web_acl.fail2",
            'aws_wafv2_web_acl.fail',
            'aws_wafv2_web_acl.fail2',
            'aws_wafregional_web_acl.fail',
            'aws_wafregional_web_acl.fail2',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 6)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
