import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.aws.EBSEncryption import scanner


class TestS3Encryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'availability_zone': ['us-west-2a'], 'size': [40]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf =  {'availability_zone': ['us-west-2a'], 'size': [40],  'encrypted': [True]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
