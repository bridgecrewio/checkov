import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.azure.AzureManagedDiscEncryption import scanner


class TestAzureManagedDiscEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'encryption_settings': [{'enabled': [False]}]}

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        def test_failure(self):
            resource_conf =  {'encryption_settings': [{'enabled': [True]}]}
            scan_result = scanner.scan_resource_conf(conf=resource_conf)
            self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
