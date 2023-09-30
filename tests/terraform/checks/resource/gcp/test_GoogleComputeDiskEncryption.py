import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeDiskEncryption import check
from checkov.common.models.enums import CheckResult


class TestGoogleComputeDiskEncryption(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_disk" "default" {
              name  = "test-disk"
              type  = "pd-ssd"
              zone  = "us-central1-a"
              image = "debian-8-jessie-v20170523"
              physical_block_size_bytes = 4096
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_disk']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_disk" "default" {
              name  = "test-disk"
              type  = "pd-ssd"
              zone  = "us-central1-a"
              image = "debian-8-jessie-v20170523"
              physical_block_size_bytes = 4096
              disk_encryption_key {
                raw_key = "acXTX3rxrKAFTF0tYVLvydU1riRZTvUNC4g5I11NY-c="  # checkov:skip=CKV_SECRET_6 test secret
                }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_disk']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
