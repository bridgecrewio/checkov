import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.FrontDoorWAFACLCVE202144228 import check
from checkov.terraform.runner import Runner


class TestFrontDoorWAFACLCVE202144228(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_FrontDoorWAFACLCVE202144228"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_frontdoor_firewall_policy.dsr_1_1_default",
            "azurerm_frontdoor_firewall_policy.dsr_1_0_default",
            "azurerm_frontdoor_firewall_policy.dsr_1_1_enabled_block",
            "azurerm_frontdoor_firewall_policy.dsr_1_1_enabled_redirect",
        }
        failing_resources = {
            "azurerm_frontdoor_firewall_policy.default",
            "azurerm_frontdoor_firewall_policy.dsr_1_1_disabled",
            "azurerm_frontdoor_firewall_policy.dsr_1_1_disabled_default",
            "azurerm_frontdoor_firewall_policy.dsr_1_1_enabled_allow",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

        # check especially for the evaluated keys
        actual_evaluated_keys = next(
            c.check_result["evaluated_keys"]
            for c in report.failed_checks
            if c.resource == "azurerm_frontdoor_firewall_policy.dsr_1_1_enabled_allow"
        )
        expected_evaluated_keys = [
            "managed_rule/[0]/type",
            "managed_rule/[0]/override/[0]/rule_group_name",
            "managed_rule/[0]/override/[0]/rule/[0]/rule_id",
            "managed_rule/[0]/override/[0]/rule/[0]/enabled",
            "managed_rule/[0]/override/[0]/rule/[0]/action",
        ]
        self.assertCountEqual(expected_evaluated_keys, actual_evaluated_keys)


if __name__ == "__main__":
    unittest.main()
