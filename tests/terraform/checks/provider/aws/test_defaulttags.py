import unittest

from checkov.terraform.checks.provider.aws.defaulttags import check
from checkov.common.models.enums import CheckResult


class TestDefaultTags(unittest.TestCase):

    def test_success(self):
        provider_conf = {'region': ['us-west-2'], 'default_tags': {'tags': {'Environment': 'Test', 'Owner': 'TestOwner'}}}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        provider_conf = {'region': ['us-west-2']}
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
