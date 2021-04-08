import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AKSEnablesPrivateClusters import check
from checkov.common.models.enums import CheckResult


class TestAKSEnablesPrivateClusters(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_kubernetes_cluster" "example" {
                  name                = "example-aks1"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                  dns_prefix          = "exampleaks1"
                
                  default_node_pool {
                    name       = "default"
                    node_count = 1
                    vm_size    = "Standard_D2_v2"
                  }
                
                  identity {
                    type = "SystemAssigned"
                  }
                
                  tags = {
                    Environment = "Production"
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_kubernetes_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_kubernetes_cluster" "example" {
                  name                = "example-aks1"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                  dns_prefix          = "exampleaks1"
                  private_cluster_enabled = false
                  
                  default_node_pool {
                    name       = "default"
                    node_count = 1
                    vm_size    = "Standard_D2_v2"
                  }
                
                  identity {
                    type = "SystemAssigned"
                  }
                
                  tags = {
                    Environment = "Production"
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_kubernetes_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_kubernetes_cluster" "example" {
                  name                = "example-aks1"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                  dns_prefix          = "exampleaks1"
                  private_cluster_enabled = true
                  
                  default_node_pool {
                    name       = "default"
                    node_count = 1
                    vm_size    = "Standard_D2_v2"
                  }
                
                  identity {
                    type = "SystemAssigned"
                  }
                
                  tags = {
                    Environment = "Production"
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_kubernetes_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
