import unittest

import hcl2

from checkov.terraform.checks.resource.azure.KeyvaultRecoveryEnabled import check
from checkov.common.models.enums import CheckResult


class TestKeyVaultRecoveryEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "testvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              sku_name = "standard"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "testvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              soft_delete_enabled         = false
              sku_name = "standard"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "testvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              soft_delete_enabled         = true
              purge_protection_enabled    = true
              sku_name = "standard"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault" "example" {
              name                        = "testvault"
              location                    = azurerm_resource_group.example.location
              resource_group_name         = azurerm_resource_group.example.name
              enabled_for_disk_encryption = true
              tenant_id                   = data.azurerm_client_config.current.tenant_id
              purge_protection_enabled    = true
              sku_name = "standard"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
