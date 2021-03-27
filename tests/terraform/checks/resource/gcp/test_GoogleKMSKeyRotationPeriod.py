import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleKMSRotationPeriod import check


class TestGoogleKMSKeyRotationPeriod(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "google_kms_crypto_key" "key" {
              name            = "crypto-key-example"
              key_ring        = google_kms_key_ring.keyring.id
              lifecycle {
                prevent_destroy = true
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_kms_crypto_key"]["key"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "google_kms_crypto_key" "key" {
              name            = "crypto-key-example"
              key_ring        = google_kms_key_ring.keyring.id
              rotation_period = "100000s"
              lifecycle {
                prevent_destroy = true
              }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["google_kms_crypto_key"]["key"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
