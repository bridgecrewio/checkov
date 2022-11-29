import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.APIManagementMinTLS12 import check
from checkov.terraform.runner import Runner


class TestAPIManagementMinTLS12(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_APIManagementMinTLS12"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_api_management.pass",
        }

        failing_resources = {
            "azurerm_api_management.fail",
            "azurerm_api_management.fail2",
            "azurerm_api_management.fail3",
            "azurerm_api_management.fail4",
            "azurerm_api_management.fail5",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passed_check_resources))
        self.assertEqual(summary["failed"], len(failed_check_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
