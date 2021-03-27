import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleStorageBucketUniformAccess import check


class TestGoogleStorageBucketUniformAccess(unittest.TestCase):
    def test_failure_default(self):
        hcl_res = hcl2.loads(
            """
                resource "google_storage_bucket" "static-site" {
                  name          = "image-store.com"
                  location      = "EU"
                  force_destroy = true
                }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_storage_bucket"]["static-site"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_explicit(self):
        hcl_res = hcl2.loads(
            """
                         resource "google_storage_bucket" "static-site" {
                           name          = "image-store.com"
                           location      = "EU"
                           force_destroy = true
                           uniform_bucket_level_access = false
                         }
                         """
        )
        resource_conf = hcl_res["resource"][0]["google_storage_bucket"]["static-site"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_bucket_uniform(self):
        hcl_res = hcl2.loads(
            """
                         resource "google_storage_bucket" "static-site" {
                           name          = "image-store.com"
                           location      = "EU"
                           force_destroy = true
                           uniform_bucket_level_access = true
                         }
                         """
        )
        resource_conf = hcl_res["resource"][0]["google_storage_bucket"]["static-site"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
