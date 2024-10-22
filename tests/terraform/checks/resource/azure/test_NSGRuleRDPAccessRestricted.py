import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.NSGRuleRDPAccessRestricted import check
from checkov.terraform.runner import Runner


class TestNSGRuleRDPAccessRestricted(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_NSGRuleRDPAccessRestricted"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_network_security_rule.https",
            "azurerm_network_security_rule.rdp_restricted_prefixes",
            "azurerm_network_security_group.rdp_restricted",
            "azurerm_network_security_group.snet_nsgs"
        }
        failing_resources = {
            "azurerm_network_security_rule.all",
            "azurerm_network_security_rule.range",
            "azurerm_network_security_rule.ranges_prefixes",
            "azurerm_network_security_rule.rdp",
            "azurerm_network_security_group.ranges",
            "azurerm_network_security_rule.ranges_prefixes_lower_case",
            "azurerm_network_security_rule.range_prefix_lower_case",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 7)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
