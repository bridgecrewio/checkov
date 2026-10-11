import unittest

from checkov.terraform.checks.resource.gcp.GoogleCloudDNSKeySpecsRSASHA1 import check
from checkov.common.models.enums import CheckResult


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
    def test_unknown_unresolved_key_spec(self):
        resource_conf = {
            "dnssec_config": [{"default_key_specs": ["${default_key_specs.value.algorithm}"]}]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_failure_takes_precedence_over_unresolved_key_spec(self):
        resource_conf = {
            "dnssec_config": [{
                "default_key_specs": [
                    "${default_key_specs.value.algorithm}",
                    {"algorithm": ["rsasha1"]},
                ]
            }]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
