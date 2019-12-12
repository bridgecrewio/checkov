import unittest

from checkov.terraform.checks.resource.aws.EBSSnapshotEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestEBSSnapshotEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'availability_zone': ['us-west-2a'], 'size': [40]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf =  {'availability_zone': ['us-west-2a'], 'size': [40],  'encrypted': [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
