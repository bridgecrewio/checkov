import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.AzureServicebusDoubleEncryptionEnabled import check
from checkov.terraform.runner import Runner


class TestAzureServicebusDoubleEncryptionEnabled(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_AzureServicebusDoubleEncryptionEnabled"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "azurerm_servicebus_namespace.pass",
        }
        failing_resources = {
            "azurerm_servicebus_namespace.fail",
            "azurerm_servicebus_namespace.fail2",
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
