import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleComputeInstanceOSLogin import check


class TestGoogleComputeInstanceOSLogin(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
              metadata = {
                 enable-oslogin = false
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
              metadata = {
                 foo = "bar"
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
              metadata = {
                 enable-oslogin = true
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
