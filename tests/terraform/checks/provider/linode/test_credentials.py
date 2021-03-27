import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.provider.linode.credentials import check


class TestCredentials(unittest.TestCase):
    def test_success(self):
        provider_conf = {}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        provider_conf = {
            "token": [
                "c7680462065ee80d0fef2940784b1af6826f6e0b18586194c5f67c4b40fa7f09"
            ]
        }
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
