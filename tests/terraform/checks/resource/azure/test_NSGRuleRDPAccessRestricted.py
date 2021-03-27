import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.NSGRuleRDPAccessRestricted import check


class TestNSGRuleRDPAccessRestricted(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_network_security_rule" "example" {
              name                        = "test123"
              priority                    = 100
              direction                   = "Inbound"
              access                      = "Allow"
              protocol                    = "TCP"
              source_port_range           = "*"
              destination_port_range      = ["3380-3390", "22"]
              source_address_prefix       = "*"
              destination_address_prefix  = "*"
              resource_group_name         = azurerm_resource_group.example.name
              network_security_group_name = azurerm_network_security_group.example.name
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_network_security_rule"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_case_insensitive(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_network_security_rule" "example" {
              name                        = "test123"
              priority                    = 100
              direction                   = "inbound"
              access                      = "allow"
              protocol                    = "Tcp"
              source_port_range           = "*"
              destination_port_range      = ["3380-3390", "22"]
              source_address_prefix       = "Internet"
              destination_address_prefix  = "*"
              resource_group_name         = azurerm_resource_group.example.name
              network_security_group_name = azurerm_network_security_group.example.name
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_network_security_rule"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
                    resource "azurerm_network_security_rule" "example" {
                      name                        = "test123"
                      priority                    = 100
                      direction                   = "Inbound"
                      access                      = "Deny"
                      protocol                    = "TCP"
                      source_port_range           = "*"
                      destination_port_range      = ["3389"]
                      source_address_prefix       = "*"
                      destination_address_prefix  = "*"
                      resource_group_name         = azurerm_resource_group.example.name
                      network_security_group_name = azurerm_network_security_group.example.name
                    }
                        """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_network_security_rule"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads(
            """
        resource "azurerm_network_security_group" "tfer--Second-002D-nsg" {
          location            = "eastus"
          name                = "Second-nsg"
          resource_group_name = "Ariel"

          security_rule {
            access                     = "Allow"
            destination_address_prefix = "*"
            destination_port_range     = "3389"
            direction                  = "Inbound"
            name                       = "RDP"
            priority                   = "300"
            protocol                   = "*"
            source_address_prefix      = "*"
            source_port_range          = "*"
          }
        }
        """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_network_security_group"][
            "tfer--Second-002D-nsg"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
