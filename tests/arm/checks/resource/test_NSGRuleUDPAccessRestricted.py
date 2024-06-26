import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.arm.checks.resource.NSGRuleUDPAccessRestricted import check
from checkov.arm.runner import Runner


class TestNSGRuleUDPAccessRestricted(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_NSGRuleUDPAccessRestricted"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Network/networkSecurityGroups/securityRules.rulePass",
            "Microsoft.Network/networkSecurityGroups/securityRules.rulePass2",
            "Microsoft.Network/networkSecurityGroups/securityRules.rulePass3",
            "Microsoft.Network/networkSecurityGroups.pass",
            "Microsoft.Network/networkSecurityGroups.pass2",
            "Microsoft.Network/networkSecurityGroups.pass3",
        }
        failing_resources = {
            "Microsoft.Network/networkSecurityGroups/securityRules.ruleFail",
            "Microsoft.Network/networkSecurityGroups/securityRules.ruleFail2",
            "Microsoft.Network/networkSecurityGroups/securityRules.ruleFail3",
            "Microsoft.Network/networkSecurityGroups/securityRules.ruleFail4",
            "Microsoft.Network/networkSecurityGroups/securityRules.ruleFail5",
            "Microsoft.Network/networkSecurityGroups.fail",
            "Microsoft.Network/networkSecurityGroups.fail2",
            "Microsoft.Network/networkSecurityGroups.fail3",
            "Microsoft.Network/networkSecurityGroups.fail4",
            "Microsoft.Network/networkSecurityGroups.fail5",
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
