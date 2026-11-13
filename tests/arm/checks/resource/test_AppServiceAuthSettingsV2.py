import unittest
from pathlib import Path

from checkov.arm.checks.resource.AppServiceAuthentication import check as auth_check
from checkov.arm.checks.resource.AppServiceDetailedErrorMessagesEnabled import check as detailed_errors_check
from checkov.arm.checks.resource.AppServiceDotnetFrameworkVersion import check as dotnet_check
from checkov.arm.checks.resource.AppServiceEnableFailedRequest import check as failed_request_check
from checkov.arm.checks.resource.AppServiceHttpLoggingEnabled import check as http_logging_check
from checkov.arm.checks.resource.AppServicePublicAccessDisabled import check as public_access_check
from checkov.arm.checks.resource.AppServiceUsedAzureFiles import check as azure_files_check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter

TEST_FILES_DIR = Path(__file__).parent / "example_AppServiceAuthSettingsV2"

AUTH_V2_EXPRESSION = "Microsoft.Web/sites/config.[format('{0}/{1}', parameters('appName'), 'authsettingsV2')]"
AUTH_V2_DISABLED = "Microsoft.Web/sites/config.disabled-app/authsettingsV2"
AUTH_LEGACY = "Microsoft.Web/sites/config.legacy-app/authsettings"
WEB_CONFIG = "Microsoft.Web/sites/config.web-app/web"


class TestAppServiceAuthSettingsV2(unittest.TestCase):
    @staticmethod
    def _run(check_id):
        report = Runner().run(root_folder=str(TEST_FILES_DIR), runner_filter=RunnerFilter(checks=[check_id]))
        passed = {c.resource for c in report.passed_checks}
        failed = {c.resource for c in report.failed_checks}
        return report, passed, failed

    def test_authentication_reads_platform_enabled(self):
        report, passed, failed = self._run(auth_check.id)

        self.assertIn(AUTH_V2_EXPRESSION, passed)
        self.assertIn(AUTH_LEGACY, passed)
        self.assertIn("config.authsettingsV2", passed)
        self.assertIn(AUTH_V2_DISABLED, failed)
        self.assertNotIn(AUTH_V2_EXPRESSION, failed)
        self.assertEqual(report.get_summary()["parsing_errors"], 0)

    def test_web_config_checks_skip_auth_settings_v2(self):
        for check in (
            http_logging_check,
            detailed_errors_check,
            failed_request_check,
            dotnet_check,
            azure_files_check,
            public_access_check,
        ):
            with self.subTest(check=check.id):
                _, passed, failed = self._run(check.id)
                evaluated = passed | failed

                self.assertNotIn(AUTH_V2_EXPRESSION, evaluated)
                self.assertNotIn(AUTH_V2_DISABLED, evaluated)
                # the regular web configuration is still evaluated
                self.assertIn(WEB_CONFIG, failed)


if __name__ == "__main__":
    unittest.main()
