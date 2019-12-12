import unittest

from checkov.terraform.checks.resource.azure.StorageAccountsTransportEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestAzureManagedDiscEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['test'], 'resource_group_name': ['${azurerm_resource_group.rg.name}'],
                         'location': ['${var.location}'], 'account_kind': ['StorageV2'], 'account_tier': ['Premium'],
                         'account_replication_type': ['LRS']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['test'], 'resource_group_name': ['${azurerm_resource_group.rg.name}'],
                         'location': ['${var.location}'], 'account_kind': ['StorageV2'],
                         'account_tier': ['Premium'], 'account_replication_type': ['LRS'],
                         'enable_https_traffic_only': [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
