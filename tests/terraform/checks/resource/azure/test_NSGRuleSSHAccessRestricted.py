import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.NSGRuleSSHAccessRestricted import check


class TestNSGRuleSSHAccessRestricted(unittest.TestCase):
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
              destination_port_range      = "22"
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
                      destination_port_range      = ["22"]
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

    def test_unknown(self):
        hcl_res = hcl2.loads(
            """
resource "azurerm_network_security_group" "mynsg" {
    name = var.nsg_name
    resource_group_name = azurerm_resource_group.rg.name
    location = var.location

    security_rule = [for rule in var.security_rules : {
        name = rule.name
        priority = rule.priority
        source_address_prefix = lookup(rule, "source_address_prefixes", []) == [] ? lookup(rule, "source_address_prefix", var.nsg_default_source_address_prefix) : ""
        source_address_prefixes = lookup(rule, "source_address_prefixes", [])
        access = lookup(rule, "access", var.nsg_default_access)
        destination_port_range = lookup(rule, "destination_port_ranges", []) == [] ? lookup(rule, "destination_port_range", var.nsg_default_destination_port_range) : ""
        destination_port_ranges = lookup(rule, "destination_port_ranges", [])
        direction = lookup(rule, "direction", var.nsg_default_direction)
        protocol = lookup(rule, "protocol", var.nsg_default_protocol)
        source_port_range = lookup(rule, "source_port_range", var.nsg_default_source_port_range)
        description = ""
        destination_address_prefix = "*"
        destination_address_prefixes = []
        destination_application_security_group_ids = []
        source_application_security_group_ids = []
        source_port_ranges = []
    }]
}
        """
        )

        resource_conf = hcl_res["resource"][0]["azurerm_network_security_group"][
            "mynsg"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)


if __name__ == "__main__":
    unittest.main()
