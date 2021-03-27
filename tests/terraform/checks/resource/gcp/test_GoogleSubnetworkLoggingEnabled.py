import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleSubnetworkLoggingEnabled import check


class TestGoogleSubnetworkLoggingEnabled(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
        resource "google_compute_subnetwork" "without logging" {
          name          = "log-test-subnetwork"
          ip_cidr_range = "10.2.0.0/16"
          region        = "us-central1"
          network       = google_compute_network.custom-test.id
        }
        """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_subnetwork"][
            "without logging"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
        resource "google_compute_subnetwork" "with logging" {
          name          = "log-test-subnetwork"
          ip_cidr_range = "10.2.0.0/16"
          region        = "us-central1"
          network       = google_compute_network.custom-test.id

          log_config {
            aggregation_interval = "INTERVAL_10_MIN"
            flow_sampling        = 0.5
            metadata             = "INCLUDE_ALL_METADATA"
          }
        }
        """
        )
        resource_conf = hcl_res["resource"][0]["google_compute_subnetwork"][
            "with logging"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
