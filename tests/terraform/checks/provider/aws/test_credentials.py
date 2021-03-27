import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.provider.aws.credentials import check


class TestCredentials(unittest.TestCase):
    def test_success(self):
        provider_conf = {"region": ["us-west-2"]}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)
        provider_conf = {}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        provider_conf = {
            "region": ["us-west-2"],
            "access_key": ["AKIAIOSFODNN7EXAMPLE"],
            "secret_key": ["wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"],
        }
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)
        provider_conf = {
            "region": ["us-west-2"],
            "secret_key": ["wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"],
        }
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)
        provider_conf = {
            "region": ["us-west-2"],
            "access_key": ["AKIAIOSFODNN7EXAMPLE"],
        }
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
