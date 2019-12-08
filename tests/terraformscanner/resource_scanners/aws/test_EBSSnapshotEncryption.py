import unittest

from checkov.terraform.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.EBSSnapshotEncryption import check


class TestEBSSnapshotEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'availability_zone': ['us-west-2a'], 'size': [40]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf =  {'availability_zone': ['us-west-2a'], 'size': [40],  'encrypted': [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
