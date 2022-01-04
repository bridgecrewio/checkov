import unittest

import hcl2

from checkov.terraform.checks.provider.linode.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):
    def test_success(self):
        hcl_res = hcl2.loads(
            """
            provider "linode" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["linode"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            provider "linode" {
                token = "c7680462065ee80d0fef2940784b1af6826f6e0b18586194c5f67c4b40fa7f09"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["linode"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
