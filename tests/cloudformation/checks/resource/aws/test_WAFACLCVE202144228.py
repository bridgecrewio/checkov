import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.WAFACLCVE202144228 import check
from checkov.cloudformation.runner import Runner
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter


class TestWAFACLCVE202144228(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_WAFACLCVE202144228"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "AWS::WAFv2::WebACL.Pass",
        }

        failing_resources = {
            "AWS::WAFv2::WebACL.NoRule",
            "AWS::WAFv2::WebACL.WrongRule",
            "AWS::WAFv2::WebACL.RuleCount",
            "AWS::WAFv2::WebACL.RuleGroupCount",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_conditional_rules(self):
        # a `Fn::If` in `Rules` can't be resolved statically
        resource_conf = {
            "Type": "AWS::WAFv2::WebACL",
            "Properties": {
                "DefaultAction": {"Allow": {}},
                "Scope": "REGIONAL",
                "Rules": {
                    "Fn::If": [
                        "SomeCondition",
                        [
                            {
                                "Name": "rule-1",
                                "Priority": 1,
                                "Statement": {
                                    "ManagedRuleGroupStatement": {
                                        "VendorName": "AWS",
                                        "Name": "AWSManagedRulesKnownBadInputsRuleSet",
                                    }
                                },
                                "OverrideAction": {"None": {}},
                            }
                        ],
                        [],
                    ]
                },
            },
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)

        self.assertEqual(CheckResult.UNKNOWN, scan_result)


if __name__ == "__main__":
    unittest.main()
