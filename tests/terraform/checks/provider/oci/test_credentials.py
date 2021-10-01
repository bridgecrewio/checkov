import unittest

from checkov.terraform.checks.provider.oci.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):

    def test_success(self):
        provider_conf = {}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        provider_conf = {'private_key_password' :['anystringwilldo']}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
