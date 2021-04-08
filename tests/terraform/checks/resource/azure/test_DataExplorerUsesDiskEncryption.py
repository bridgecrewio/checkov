import unittest

import hcl2

from checkov.terraform.checks.resource.azure.DataExplorerUsesDiskEncryption import check
from checkov.common.models.enums import CheckResult


class TestDataExplorerUsesDiskEncryption(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_kusto_cluster" "example" {
                  name                = "kustocluster"
                  location            = azurerm_resource_group.rg.location
                  resource_group_name = azurerm_resource_group.rg.name
                
                  sku {
                    name     = "Standard_D13_v2"
                    capacity = 2
                  }
                
                  tags = {
                    Environment = "Production"
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_kusto_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_kusto_cluster" "example" {
                  name                = "kustocluster"
                  location            = azurerm_resource_group.rg.location
                  resource_group_name = azurerm_resource_group.rg.name
                
                  sku {
                    name     = "Standard_D13_v2"
                    capacity = 2
                  }
                
                  tags = {
                    Environment = "Production"
                  }
                  enable_disk_encryption = false
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_kusto_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_kusto_cluster" "example" {
                  name                = "kustocluster"
                  location            = azurerm_resource_group.rg.location
                  resource_group_name = azurerm_resource_group.rg.name
                
                  sku {
                    name     = "Standard_D13_v2"
                    capacity = 2
                  }
                  tags = {
                    Environment = "Production"
                  }
                  enable_disk_encryption = true
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_kusto_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
