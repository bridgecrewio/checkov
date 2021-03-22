import unittest

import hcl2

from checkov.terraform.checks.resource.azure.EventgridDomainNetworkAccess import check
from checkov.common.models.enums import CheckResult


class TestEventgridDomainNetworkAccess(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_eventgrid_domain" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_eventgrid_domain']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_explicit(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_eventgrid_domain" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              
              public_network_access_enabled = true
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_eventgrid_domain']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_eventgrid_domain" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              
              public_network_access_enabled = false
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_eventgrid_domain']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
