import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleStorageBucketNotPublic import check
from checkov.common.models.enums import CheckResult


class TestGoogleStorageBucketNotPublic(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
        resource "google_storage_bucket_iam_member" "member" {
          bucket = google_storage_bucket.default.name
          role = "roles/storage.admin"
          member = "allUsers"
        }
                """)
        resource_conf = hcl_res['resource'][0]['google_storage_bucket_iam_member']['member']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
        resource "google_storage_bucket_iam_binding" "binding" {
          bucket = google_storage_bucket.default.name
          role = "roles/storage.admin"
          members = [
            "user:jane@example.com",
            "allAuthenticatedUsers"
          ]
        }
                """)
        resource_conf = hcl_res['resource'][0]['google_storage_bucket_iam_binding']['binding']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        hcl_res = hcl2.loads("""
                resource "google_storage_bucket_iam_member" "member" {
                  bucket = google_storage_bucket.default.name
                  role = "roles/storage.admin"
                  member = "user:jane@example.com"
                }
                        """)
        resource_conf = hcl_res['resource'][0]['google_storage_bucket_iam_member']['member']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
                resource "google_storage_bucket_iam_binding" "binding" {
                  bucket = google_storage_bucket.default.name
                  role = "roles/storage.admin"
                  members = [
                    "user:jane@example.com"
                  ]
                }
                        """)
        resource_conf = hcl_res['resource'][0]['google_storage_bucket_iam_binding']['binding']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)



if __name__ == '__main__':
    unittest.main()
