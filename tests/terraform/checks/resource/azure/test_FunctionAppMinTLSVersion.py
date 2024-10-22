import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.FunctionAppMinTLSVersion import check
from checkov.terraform.runner import Runner


class TestFunctionAppMinTLSVersion(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_FunctionAppMinTLSVersion"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "azurerm_function_app.pass",
            "azurerm_function_app.pass2",
            "azurerm_function_app.pass3",
            "azurerm_function_app_slot.pass4",
            "azurerm_linux_function_app.pass5",
            "azurerm_windows_function_app.pass6",
            "azurerm_linux_function_app_slot.pass7",
            "azurerm_windows_function_app_slot.pass8",
            "azurerm_windows_function_app_slot.pass9",
        }
        failing_resources = {
            "azurerm_function_app.fail",
            "azurerm_function_app_slot.fail2",
            "azurerm_linux_function_app.fail3",
            "azurerm_windows_function_app.fail4",
            "azurerm_linux_function_app_slot.fail5",
            "azurerm_windows_function_app_slot.fail6",
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
