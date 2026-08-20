import os
import unittest

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.azure.AppServiceAuthentication import check


class TestAppServiceAuthentication(unittest.TestCase):

    def test_non_dict_auth_settings_does_not_crash(self):
        # When auth_settings[0] is a non-dict type (e.g. a StrNode from Terraform plan JSON),
        # the check must return FAILED instead of raising TemplateAttributeError.
        conf = {"auth_settings": ["some_template_expression"]}
        result = check.scan_resource_conf(conf=conf)
        self.assertEqual(result, CheckResult.FAILED)

        conf_v2 = {"auth_settings_v2": ["some_template_expression"]}
        result_v2 = check.scan_resource_conf(conf=conf_v2)
        self.assertEqual(result_v2, CheckResult.FAILED)

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_AppServiceAuthentication")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'azurerm_app_service.pass',
            'azurerm_windows_web_app.pass',
            'azurerm_linux_web_app.pass',
            'azurerm_windows_web_app.pass2',
            'azurerm_linux_web_app.pass2',
        }
        failing_resources = {
            'azurerm_app_service.fail',
            'azurerm_app_service.fail2',
            'azurerm_windows_web_app.fail',
            'azurerm_linux_web_app.fail',
            'azurerm_windows_web_app.fail2',
            'azurerm_linux_web_app.fail2',
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