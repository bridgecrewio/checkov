import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.AppServiceSlotMinTLS import check
from checkov.terraform.runner import Runner


class TestAppServiceSlotMinTLS(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_AppServiceSlotMinTLS"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "azurerm_app_service_slot.pass",
            "azurerm_app_service_slot.pass2",
            "azurerm_app_service_slot.pass3",
        }
        failing_resources = {
            "azurerm_app_service_slot.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 7)  # 3 unknown

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
