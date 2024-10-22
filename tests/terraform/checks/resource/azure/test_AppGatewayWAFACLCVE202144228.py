import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.AppGatewayWAFACLCVE202144228 import check
from checkov.terraform.runner import Runner


class TestAppGatewayWAFACLCVE202144228(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_AppGatewayWAFACLCVE202144228"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_web_application_firewall_policy.owasp_3_1_default",
            "azurerm_web_application_firewall_policy.owasp_3_2_default",
            "azurerm_web_application_firewall_policy.version_3_1_default",
            "azurerm_web_application_firewall_policy.owasp_3_1_disabled_different",
            "azurerm_web_application_firewall_policy.empty_disabled_rules"
        }
        failing_resources = {
            "azurerm_web_application_firewall_policy.owasp_3_0",
            "azurerm_web_application_firewall_policy.owasp_3_1_disabled",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

        # check especially for the evaluated keys
        actual_evaluated_keys = next(
            c.check_result["evaluated_keys"]
            for c in report.failed_checks
            if c.resource == "azurerm_web_application_firewall_policy.owasp_3_1_disabled"
        )
        expected_evaluated_keys = [
            "managed_rules/[0]/managed_rule_set[0]/type",
            "managed_rules/[0]/managed_rule_set[0]/version",
            "managed_rules/[0]/managed_rule_set[0]/rule_group_override/[0]/rule_group_name",
            "managed_rules/[0]/managed_rule_set[0]/rule_group_override/[0]/disabled_rules",
        ]
        self.assertCountEqual(expected_evaluated_keys, actual_evaluated_keys)


if __name__ == "__main__":
    unittest.main()
