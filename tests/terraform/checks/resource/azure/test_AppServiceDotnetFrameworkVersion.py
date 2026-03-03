import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.azure.AppServiceDotnetFrameworkVersion import check


class TestAppServiceDotnetFrameworkVersion(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_AppServiceDotnetFrameworkVersion")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'azurerm_app_service.pass',    # v8.0
            'azurerm_app_service.pass2',   # v9.0
            'azurerm_app_service.pass3',   # v10.0
            'azurerm_windows_web_app.pass',   # v8.0
            'azurerm_windows_web_app.pass2',  # v9.0
            'azurerm_windows_web_app.pass3',  # v10.0
        }
        failing_resources = {
            'azurerm_app_service.fail',    # v5.0 EOL
            'azurerm_app_service.fail2',   # v6.0 EOL
            'azurerm_windows_web_app.fail',   # v2.0 EOL
            'azurerm_windows_web_app.fail2',  # v6.0 EOL
        }
        skipped_resources = {}

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
