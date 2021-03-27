import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleComputeDefaultServiceAccount import (
    check,
)


class TestGoogleComputeDefaultServiceAccount(unittest.TestCase):
    def test_failure_1(self):
        hcl_res = hcl2.loads(
            """
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
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
              service_account {
                scopes = ["userinfo-email", "compute-ro", "storage-ro"]
                email  =  "123456789-compute@developer.gserviceaccount.com"
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
              service_account {
                scopes = ["userinfo-email", "compute-ro", "storage-ro"]
                email  = "example@email.com"
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
              name         = "gke-account"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              service_account {
                scopes = ["userinfo-email", "compute-ro", "storage-ro"]
                email  =  "123456789-compute@developer.gserviceaccount.com"
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_instance"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
