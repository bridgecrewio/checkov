import unittest
from pathlib import Path
from unittest.mock import patch

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GoogleCloudDNSKeySpecsRSASHA1 import check
from checkov.terraform.runner import Runner


class TestCloudDNSKeySpecsRSASHA1(unittest.TestCase):

    def test_failure_zone_signing(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"],
                         "dnssec_config": [{
                             "state": ["on"],
                             "default_key_specs": [
                                 {"algorithm": ["rsasha1"], "key_type": ["zoneSigning"], "key_length": "1024"},
                                 {"algorithm": ["rsasha256"], "key_type": ["keySigning"], "key_length": "2048"},
                             ]
                         }]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_key_signing(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"],
                         "dnssec_config": [{
                             "state": ["on"],
                             "default_key_specs": [
                                 {"algorithm": ["rsasha256"], "key_type": ["zoneSigning"], "key_length": "1024"},
                                 {"algorithm": ["rsasha1"], "key_type": ["keySigning"], "key_length": "2048"},
                             ]
                         }]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"],
                         "dnssec_config": [{
                             "state": ["on"],
                             "default_key_specs": [
                                 {"algorithm": ["rsasha256"], "key_type": ["zoneSigning"], "key_length": "1024"},
                                 {"algorithm": ["rsasha256"], "key_type": ["keySigning"], "key_length": "2048"},
                             ]
                         }]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_default_config(self):
        resource_conf = {"name": ["example-zone"],
                         "dns_name": ["example-de13he3.com."],
                         "description": ["Example DNS zone"],
                         "dnssec_config": [{"state": ["on"]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unknown_dynamic_key_specs(self):
        resource_conf = {
            "dnssec_config": [{"default_key_specs": "default_key_specs.value.algorithm"}]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_unknown_key_specs_entry(self):
        resource_conf = {
            "dnssec_config": [{"default_key_specs": ["default_key_specs.value.algorithm"]}]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_failure_with_unknown_key_specs_entry(self):
        resource_conf = {
            "dnssec_config": [{
                "default_key_specs": [
                    "default_key_specs.value.algorithm",
                    {"algorithm": ["rsasha1"]},
                ]
            }]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_unknown_algorithm(self):
        resource_conf = {
            "dnssec_config": [{"default_key_specs": [{"algorithm": ["${var.algorithm}"]}]}]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_unknown_dnssec_config(self):
        resource_conf = {"dnssec_config": ["dnssec_config.value"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_dynamic_key_specs(self):
        test_files_dir = Path(__file__).parent / "example_GoogleCloudDNSKeySpecsRSASHA1"
        scan_results = []
        scan_resource_conf = check.scan_resource_conf

        def capture_scan_result(conf):
            scan_result = scan_resource_conf(conf)
            scan_results.append(scan_result)
            return scan_result

        with (
            patch.object(check, "scan_resource_conf", side_effect=capture_scan_result),
            patch.object(check, "log_check_error") as log_check_error,
        ):
            report = Runner().run(
                root_folder=str(test_files_dir),
                runner_filter=RunnerFilter(checks=[check.id]),
            )
        summary = report.get_summary()

        log_check_error.assert_not_called()
        self.assertEqual([CheckResult.UNKNOWN], scan_results)
        self.assertEqual(0, summary["passed"])
        self.assertEqual(0, summary["failed"])
        self.assertEqual(0, summary["parsing_errors"])
        self.assertEqual(1, summary["resource_count"])


if __name__ == '__main__':
    unittest.main()
