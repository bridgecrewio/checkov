import unittest

import hcl2

from checkov.terraform.checks.provider.panos.credentials import check
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

    def test_failure_api(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {
                api_key = "LUFRPT1yWFdyMFg5NlZxZ1ViU2ZhMTh6aGVEbDJ1UFU9ck9vc2tGcmlHV0tDbWRFa2cxcGUxSU8wMlVjaE9ReU0yYWN5SU1rL2pEOGhDcE50WEt5ABlHQWZoTm8xNG1SQQ=="
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_password(self):
        hcl_res = hcl2.loads(
            """
            provider "panos" {
                password = "changeme123!"
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["panos"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()