import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.VMCredsInCustomData import check
from checkov.terraform.runner import Runner


class TestVMCredsInCustomData(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_VMCredsInCustomData"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_virtual_machine.no_secret",
            "azurerm_virtual_machine.no_custom_data",
            "azurerm_virtual_machine.empty_os_profile",
            "azurerm_virtual_machine.no_os_profile",
        }
        failing_resources = {
            "azurerm_virtual_machine.secret",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
