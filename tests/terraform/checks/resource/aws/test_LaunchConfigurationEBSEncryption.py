import unittest

from checkov.terraform.checks.resource.aws.LaunchConfigurationEBSEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestS3Encryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'image_id': ['ami-123'], 'instance_type': ['t2.micro'],
                         'root_block_device': [{'encrypted': [False]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_missing_element(self):
        resource_conf = {'image_id': ['ami-123'], 'instance_type': ['t2.micro'], 'root_block_device': [{}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'image_id': ['ami-123'], 'instance_type': ['t2.micro'],
                         'root_block_device': [{'encrypted': [True]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
