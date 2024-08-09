import unittest

import hcl2

from checkov.terraform.checks.provider.awscc.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):
    def test_success_empty(self):
        hcl_res = hcl2.loads(
            """
            provider "awscc" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["awscc"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_region(self):
        hcl_res = hcl2.loads(
            """
            provider "awscc" {
                region = "us-west-2"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["awscc"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_both_keys(self):
        hcl_res = hcl2.loads(
            """
            provider "awscc" {
                region     = "us-west-2"
                access_key = "AKIAIOSFODNN7EXAMPLE"
                secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["awscc"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_access_key(self):
        hcl_res = hcl2.loads(
            """
            provider "awscc" {
                region     = "us-west-2"
                access_key = "AKIAIOSFODNN7EXAMPLE"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["awscc"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_secret_key(self):
        hcl_res = hcl2.loads(
            """
            provider "awscc" {
                region     = "us-west-2"
                secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["awscc"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
