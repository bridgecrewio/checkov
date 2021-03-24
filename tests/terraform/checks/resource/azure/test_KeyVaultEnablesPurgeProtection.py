import unittest

import hcl2

from checkov.terraform.checks.resource.azure.KeyVaultEnablesPurgeProtection import check
from checkov.common.models.enums import CheckResult


class TestKeyVaultEnablesPurgeProtection(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "examplekeyvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              soft_delete_retention_days  = 7
            
              sku_name = "standard"
              
              access_policy {
                tenant_id = data.azurerm_client_config.current.tenant_id
                object_id = data.azurerm_client_config.current.object_id
            
                key_permissions = [
                  "Get",
                ]
                
                secret_permissions = [
                  "Get",
                ]
            
                storage_permissions = [
                  "Get",
                ]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "examplekeyvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              soft_delete_retention_days  = 7
              purge_protection_enabled    = false
            
              sku_name = "standard"
              
              access_policy {
                tenant_id = data.azurerm_client_config.current.tenant_id
                object_id = data.azurerm_client_config.current.object_id
            
                key_permissions = [
                  "Get",
                ]
                
                secret_permissions = [
                  "Get",
                ]
            
                storage_permissions = [
                  "Get",
                ]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "examplekeyvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              soft_delete_retention_days  = 7
              purge_protection_enabled    = true
            
              sku_name = "standard"
            
              access_policy {
                tenant_id = data.azurerm_client_config.current.tenant_id
                object_id = data.azurerm_client_config.current.object_id
            
                key_permissions = [
                  "Get",
                ]
            
                secret_permissions = [
                  "Get",
                ]
            
                storage_permissions = [
                  "Get",
                ]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
