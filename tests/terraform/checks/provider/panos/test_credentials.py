import os
import unittest

import hcl2

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.provider.panos.credentials import check
from checkov.common.models.enums import CheckResult
from checkov.terraform.runner import Runner


class TestCredentials(unittest.TestCase):
    def test_success(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_api(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {
                api_key = "LUFRPT1yWFdyMFg5NlZxZ1ViU2ZhMTh6aGVEbDJ1UFU9ck9vc2tGcmlHV0tDbWRFa2cxcGUxSU8wMlVjaE9ReU0yYWN5SU1rL2pEOGhDcE50WEt5ABlHQWZoTm8xNG1SQQ=="
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_password(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {
                password = "changeme123!"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_api_key(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/resources/api_key"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources_files = {
            "/pass.tf",
        }

        failing_resources_files = {
            "/fail1.tf",
            "/fail2.tf"
        }

        passed_check_resources_files = set([c.file_path for c in report.passed_checks])
        failing_check_resources_files = set([c.file_path for c in report.failed_checks])

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources_files, passed_check_resources_files)
        self.assertEqual(failing_resources_files, failing_check_resources_files)


if __name__ == '__main__':
    unittest.main()
