import unittest

from checkov.terraform.checks.resource.gcp.GoogleCloudDNSSECEnabled import check
from checkov.common.models.enums import CheckResult


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


if __name__ == '__main__':
    unittest.main()
