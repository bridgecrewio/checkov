import unittest

import hcl2

from checkov.terraform.checks.provider.oci.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):
    def test_success(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {
                private_key_password = "anystringwilldo"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
