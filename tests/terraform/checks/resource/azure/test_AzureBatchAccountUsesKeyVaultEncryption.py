import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AzureBatchAccountUsesKeyVaultEncryption import check
from checkov.common.models.enums import CheckResult


class TestAzureBatchAccountUsesKeyVaultEncryption(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_batch_account" "example" {
              name                 = "testbatchaccount"
              resource_group_name  = azurerm_resource_group.example.name
              location             = azurerm_resource_group.example.location
              pool_allocation_mode = "BatchService"
              storage_account_id   = azurerm_storage_account.example.id
            
              tags = {
                env = "test"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_batch_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_batch_account" "example" {
              name                 = "testbatchaccount"
              resource_group_name  = azurerm_resource_group.example.name
              location             = azurerm_resource_group.example.location
              pool_allocation_mode = "BatchService"
              storage_account_id   = azurerm_storage_account.example.id
              key_vault_reference {
                id = "test"
                url = "https://test.com"
              }
            
              tags = {
                env = "test"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_batch_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
