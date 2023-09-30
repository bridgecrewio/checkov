import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.NSGRuleUDPAccessRestricted import check
from checkov.terraform.runner import Runner


class TestNSGRuleUDPAccessRestricted(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_NSGRuleUDPAccessRestricted"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_network_security_rule.pass",
            "azurerm_network_security_rule.pass2",
            "azurerm_network_security_rule.pass3",
            "azurerm_network_security_group.pass",
            "azurerm_network_security_group.pass2",
            "azurerm_network_security_group.pass3",
        }
        failing_resources = {
            "azurerm_network_security_rule.fail",
            "azurerm_network_security_rule.fail2",
            "azurerm_network_security_rule.fail3",
            "azurerm_network_security_rule.fail4",
            "azurerm_network_security_rule.fail5",

            "azurerm_network_security_group.fail",
            "azurerm_network_security_group.fail2",
            "azurerm_network_security_group.fail3",
            "azurerm_network_security_group.fail4",
            "azurerm_network_security_group.fail5",
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
