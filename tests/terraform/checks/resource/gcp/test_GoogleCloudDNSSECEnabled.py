import os
import unittest

from checkov.terraform.checks.resource.gcp.GoogleCloudDNSSECEnabled import check
from checkov.common.models.enums import CheckResult
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCloudDNSSECEnabled(unittest.TestCase):

    def test_failure_no_config(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_wrong_config(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"],
                         "dnssec_config": [{"state": ["off"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"],
                         "dnssec_config": [{"state": ["on"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_visibility_check(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/test_GoogleCloudDNSSECEnabled"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
