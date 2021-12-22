import unittest

import hcl2

from checkov.terraform.checks.resource.azure.CognitiveServicesDisablesPublicNetwork import check
from checkov.common.models.enums import CheckResult


class TestCognitiveServicesDisablesPublicNetwork(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_cognitive_account" "examplea" {
  name                = "example-account"
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  kind                = "Face"

  public_network_access_enabled = true

  sku_name = "S0"
}
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_cognitive_account']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_missing_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_cognitive_account" "examplea" {
  name                = "example-account"
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  kind                = "Face"

  sku_name = "S0"
}
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_cognitive_account']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)
        
    def test_success(self):
        hcl_res = hcl2.loads("""
resource "azurerm_cognitive_account" "examplea" {
  name                = "example-account"
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name
  kind                = "Face"

  public_network_access_enabled = false

  sku_name = "S0"
}
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_cognitive_account']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
