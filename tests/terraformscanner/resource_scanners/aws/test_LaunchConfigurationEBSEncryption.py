import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.aws.LaunchConfigurationEBSEncryption import scanner


class TestS3Encryption(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'image_id': ['ami-123'], 'instance_type': ['t2.micro'], 'root_block_device': [{'encrypted': [False]}]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf =  {'image_id': ['ami-123'], 'instance_type': ['t2.micro'], 'root_block_device': [{'encrypted': [True]}]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
