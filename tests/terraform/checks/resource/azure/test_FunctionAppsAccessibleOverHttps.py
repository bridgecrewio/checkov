import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.FunctionAppsAccessibleOverHttps import check
from checkov.terraform.runner import Runner


class TestFunctionAppsAccessibleOverHttps(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_FunctionAppAccessibleOverHttps"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "azurerm_function_app.pass",
            "azurerm_function_app_slot.pass",
            "azurerm_linux_function_app.pass",
            "azurerm_linux_function_app.pass2",
            "azurerm_linux_function_app_slot.pass",
            "azurerm_linux_function_app_slot.pass2",
        }
        failing_resources = {
            "azurerm_function_app.fail",
            "azurerm_function_app.fail2",
            "azurerm_function_app_slot.fail",
            "azurerm_function_app_slot.fail2",
            "azurerm_linux_function_app.fail",
            "azurerm_linux_function_app.fail2",
            "azurerm_linux_function_app.fail3",
            "azurerm_linux_function_app_slot.fail",
            "azurerm_linux_function_app_slot.fail2",
            "azurerm_linux_function_app_slot.fail3",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_tf_plan(self):
        test_files_dir = Path(__file__).parent / "example_FunctionAppAccessibleOverHttps_tfplan"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary["failed"], 1)
        self.assertEqual(report.failed_checks[0].check_id, 'CKV_AZURE_70')


if __name__ == '__main__':
    unittest.main()
