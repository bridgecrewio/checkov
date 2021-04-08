import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AzureContainerGroupDeployedIntoVirtualNetwork import check
from checkov.common.models.enums import CheckResult


class TestAzureContainerGroupDeployedIntoVirtualNetwork(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_container_group" "example" {
              name                = "example-continst"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              ip_address_type     = "public"
              dns_name_label      = "aci-label"
              os_type             = "Linux"
            
              container {
                name   = "hello-world"
                image  = "microsoft/aci-helloworld:latest"
                cpu    = "0.5"
                memory = "1.5"
            
                ports {
                  port     = 443
                  protocol = "TCP"
                }
              }
            
              container {
                name   = "sidecar"
                image  = "microsoft/aci-tutorial-sidecar"
                cpu    = "0.5"
                memory = "1.5"
              }    
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_container_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_container_group" "example" {
              name                = "example-continst"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              ip_address_type     = "public"
              dns_name_label      = "aci-label"
              os_type             = "Linux"
            
              container {
                name   = "hello-world"
                image  = "microsoft/aci-helloworld:latest"
                cpu    = "0.5"
                memory = "1.5"
            
                ports {
                  port     = 443
                  protocol = "TCP"
                }
              }
            
              container {
                name   = "sidecar"
                image  = "microsoft/aci-tutorial-sidecar"
                cpu    = "0.5"
                memory = "1.5"
              }
              
              network_profile_id = "network_profile_id"    
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_container_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
