import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AzureSearchPublicNetworkAccessDisabled import check
from checkov.common.models.enums import CheckResult


class TestAzureSearchPublicNetworkAccessDisabled(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_search_service" "example" {
              name                = "example-search-service"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              sku                 = "standard"
              public_network_access_enabled = true
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_search_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_search_service" "example" {
              name                = "example-search-service"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              sku                 = "standard"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_search_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_search_service" "example" {
              name                = "example-search-service"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              sku                 = "standard"
              public_network_access_enabled = false
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_search_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
