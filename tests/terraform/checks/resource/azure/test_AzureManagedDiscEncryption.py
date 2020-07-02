import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AzureManagedDiscEncryption import check


class TestAzureManagedDiscEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'encryption_settings': [{'enabled': [False]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'encryption_settings': [{'enabled': [True]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
