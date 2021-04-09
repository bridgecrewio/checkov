import unittest

import hcl2

from checkov.terraform.checks.resource.azure.StorageAccountDisablePublicAccess import check
from checkov.common.models.enums import CheckResult


class TestStorageAccountDisablePublicAccess(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "storageaccountname"
              resource_group_name      = azurerm_resource_group.example.name
              location                 = azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              enable_https_traffic_only = false
              allow_blob_public_access = true

              tags = {
                environment = "staging"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "storageaccountname"
              resource_group_name      = azurerm_resource_group.example.name
              location                 = azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"

              tags = {
                environment = "staging"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "storageaccountname"
              resource_group_name      = azurerm_resource_group.example.name
              location                 = azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              allow_blob_public_access = false

              tags = {
                environment = "staging"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
