import unittest

from checkov.terraformscanner.models.enums import ScanResult
from checkov.terraformscanner.resource_scanners.gcp.GoogleStorageBucketEncryption import scanner


class TestGoogleStorageBucketEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['my-bucket'],
                         'location': ['EU']
                         }

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf = {'name': ['my-bucket'],
                         'location': ['EU'],
                         'encryption': [{'default_kms_key_name': ['foo']}]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
