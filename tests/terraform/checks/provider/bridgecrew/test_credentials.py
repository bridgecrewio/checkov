import unittest

from checkov.terraform.checks.provider.bridgecrew.credentials import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):

    def test_success(self):
        provider_conf = {}

        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        provider_conf = {'token' :['80e54890-f282-4595-ab3d-45f9bd874987']}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
