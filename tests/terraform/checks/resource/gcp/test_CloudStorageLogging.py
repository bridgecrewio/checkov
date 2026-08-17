import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.CloudStorageLogging import check


class TestCloudStorageLogging(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "google_storage_bucket" "logging" {
                name     = "jgwloggingbucket"
                location = var.location
                uniform_bucket_level_access = true
          }
        """)
        resource_conf = hcl_res['resource'][0]['google_storage_bucket']['logging']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "google_storage_bucket" "logging" {
                name     = "jgwloggingbucket"
                location = var.location
                uniform_bucket_level_access = true
                logging {
                  log_bucket = "mylovelybucket"
                }
          }
        """)
        resource_conf = hcl_res['resource'][0]['google_storage_bucket']['logging']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_computed_log_bucket(self):
        # When log_bucket references a computed value it is absent from the plan JSON
        resource_conf = {
            "name": ["my-bucket"],
            "logging": [{"log_object_prefix": "my-prefix/"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

if __name__ == '__main__':
    unittest.main()
