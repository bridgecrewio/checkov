import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.CloudStorageSelfLogging import check


class TestCloudStorageSelfLogging(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
                resource "google_storage_bucket" "static-site" {
                  name          = "image-store.com"
                  location      = "EU"
                  force_destroy = true
                  logging {
                    log_bucket="image-store.com"
                  }
                }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_storage_bucket"]["static-site"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
                         resource "google_storage_bucket" "static-site" {
                           name          = "image-store.com"
                           location      = "EU"
                           force_destroy = true
                           uniform_bucket_level_access = true
                           logging {
                             log_bucket="mybestbucket"
                             }
                         }
                         """
        )
        resource_conf = hcl_res["resource"][0]["google_storage_bucket"]["static-site"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
