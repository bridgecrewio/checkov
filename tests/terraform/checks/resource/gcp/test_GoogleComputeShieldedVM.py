import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleComputeShieldedVM import check


class TestGoogleComputeShieldedVM(unittest.TestCase):
    def test_failure_1(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
                shielded_instance_config {
                    enable_integrity_monitoring = false
                    }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              boot_disk {}
              shielded_instance_config {}
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
