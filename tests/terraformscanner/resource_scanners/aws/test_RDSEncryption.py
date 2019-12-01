import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.aws.RDSEncryption import scanner


class TestRDSEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'engine': ['postgres'], 'engine_version': ['9.6.3'], 'multi_az': [False], 'backup_retention_period': [10], 'auto_minor_version_upgrade': [True], 'storage_encrypted': [False]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf =  {'engine': ['postgres'], 'engine_version': ['9.6.3'], 'multi_az': [False], 'backup_retention_period': [10], 'auto_minor_version_upgrade': [True], 'storage_encrypted': [True]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
