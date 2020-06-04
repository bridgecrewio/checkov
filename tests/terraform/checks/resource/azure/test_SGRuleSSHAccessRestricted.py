import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SGRuleSSHAccessRestricted import check
from checkov.common.models.enums import CheckResult


class TestSGRuleSSHAccessRestricted(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
              name                        = "test123"
              priority                    = 100
              direction                   = "Inbound"
              access                      = "Allow"
              protocol                    = "TCP"
              source_port_range           = "*"
              destination_port_range      = "22"
              source_address_prefix       = "*"
              destination_address_prefix  = "*"
              resource_group_name         = azurerm_resource_group.example.name
              network_security_group_name = azurerm_network_security_group.example.name
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "azurerm_network_security_rule" "example" {
                      name                        = "test123"
                      priority                    = 100
                      direction                   = "Inbound"
                      access                      = "Deny"
                      protocol                    = "TCP"
                      source_port_range           = "*"
                      destination_port_range      = ["22"]
                      source_address_prefix       = "*"
                      destination_address_prefix  = "*"
                      resource_group_name         = azurerm_resource_group.example.name
                      network_security_group_name = azurerm_network_security_group.example.name
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)



if __name__ == '__main__':
    unittest.main()
