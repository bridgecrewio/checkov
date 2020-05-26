import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeSSLPolicy import check
from checkov.common.models.enums import CheckResult


class TestGoogleComputeSSLPolicy(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
                resource "google_compute_ssl_policy" "modern-profile" {
                  name            = "nonprod-ssl-policy"
                  profile         = "MODERN"
                }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_ssl_policy']['modern-profile']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
                        resource "google_compute_ssl_policy" "custom-profile" {
                          name            = "custom-ssl-policy"
                          min_tls_version = "TLS_1_2"
                          profile         = "CUSTOM"
                          custom_features = ["TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384", "TLS_RSA_WITH_AES_256_GCM_SHA384"]
                        }
                        """)
        resource_conf = hcl_res['resource'][0]['google_compute_ssl_policy']['custom-profile']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        hcl_res = hcl2.loads("""
                        resource "google_compute_ssl_policy" "modern-profile" {
                          name            = "nonprod-ssl-policy"
                          profile         = "MODERN"
                          min_tls_version = "TLS_1_2"
                        }
                        """)
        resource_conf = hcl_res['resource'][0]['google_compute_ssl_policy']['modern-profile']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
                        resource "google_compute_ssl_policy" "custom-profile" {
                          name            = "custom-ssl-policy"
                          min_tls_version = "TLS_1_2"
                          profile         = "CUSTOM"
                          custom_features = ["TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384", "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"]
                        }
                        """)
        resource_conf = hcl_res['resource'][0]['google_compute_ssl_policy']['custom-profile']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
