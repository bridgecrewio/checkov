import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeExternalIP import check
from checkov.common.models.enums import CheckResult


class TestGoogleComputeExternalIP(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
              access_config {
                network_tier = "STANDARD"
                }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
