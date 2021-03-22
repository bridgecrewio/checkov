import unittest

import hcl2

from checkov.terraform.checks.resource.azure.DataLakeStoreEncryption import check
from checkov.common.models.enums import CheckResult


class TestDataLakeStoreEncryption(unittest.TestCase):

    def test_failure_explicit(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_data_lake_store" "example" {
              name                = "consumptiondatalake"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              
              encryption_state = "Disabled"
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_data_lake_store']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_data_lake_store" "example" {
              name                = "consumptiondatalake"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_data_lake_store']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_explicit(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_data_lake_store" "example" {
              name                = "consumptiondatalake"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              
              encryption_state = "Enabled"
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_data_lake_store']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
