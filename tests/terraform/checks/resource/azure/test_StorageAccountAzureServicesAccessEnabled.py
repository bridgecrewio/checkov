import unittest

import hcl2

from checkov.terraform.checks.resource.azure.StorageAccountAzureServicesAccessEnabled import check
from checkov.common.models.enums import CheckResult


class TestStorageAccountAzureServicesAccessEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account_network_rules" "test" {
              resource_group_name  = azurerm_resource_group.test.name
              storage_account_name = azurerm_storage_account.test.name
            
              default_action             = "Deny"
              ip_rules                   = ["127.0.0.1"]
              virtual_network_subnet_ids = [azurerm_subnet.test.id]
              bypass                     = ["Metrics"]
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account_network_rules']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              network_rules {
                default_action             = "Deny"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
                bypass                     = ["Metrics", "AzureServices"]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
