import unittest

import hcl2

from checkov.terraform.checks.resource.azure.NSGRuleUDPAccessRestricted import check
from checkov.common.models.enums import CheckResult


class TestNSGRuleUDPAccessRestricted(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_group" "example" {
              name                = "acceptanceTestSecurityGroup1"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
            
              security_rule {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "*"
                destination_address_prefix = "*"
              }
            
              tags = {
                environment = "Production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_group" "example" {
              name                = "acceptanceTestSecurityGroup1"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
            
              security_rule {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "any"
                destination_address_prefix = "*"
              }
            
              tags = {
                environment = "Production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure3(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_group" "example" {
              name                = "acceptanceTestSecurityGroup1"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name

              security_rule {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "<nw>/0"
                destination_address_prefix = "*"
              }

              tags = {
                environment = "Production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure4(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_group" "example" {
              name                = "acceptanceTestSecurityGroup1"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name

              security_rule {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "/0"
                destination_address_prefix = "*"
              }

              tags = {
                environment = "Production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure5(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_group" "example" {
              name                = "acceptanceTestSecurityGroup1"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name

              security_rule {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "Internet"
                destination_address_prefix = "*"
              }

              tags = {
                environment = "Production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_group" "example" {
              name                = "acceptanceTestSecurityGroup1"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
            
              security_rule {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Deny"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "*"
                destination_address_prefix = "*"
              }
            
              tags = {
                environment = "Production"
              }
            }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_network_security_group" "example" {
  name                = "acceptanceTestSecurityGroup1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  security_rule {
    name                       = "test123"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Udp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    environment = "Production"
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success3(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_network_security_group" "example" {
          name                = "acceptanceTestSecurityGroup1"
          location            = azurerm_resource_group.example.location
          resource_group_name = azurerm_resource_group.example.name
        
          security_rule {
            name                       = "test123"
            priority                   = 100
            direction                  = "Inbound"
            access                     = "Allow"
            protocol                   = "Tcp"
            source_port_range          = "*"
            destination_port_range     = "*"
            source_address_prefix      = "*"
            destination_address_prefix = "*"
          }
        
          tags = {
            environment = "Production"
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_rule_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "*"
                destination_address_prefix = "*"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_rule_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "any"
                destination_address_prefix = "*"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_rule_3(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "<nw>/0"
                destination_address_prefix = "*"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_rule_4(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "/0"
                destination_address_prefix = "*"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_rule_5(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Allow"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "Internet"
                destination_address_prefix = "*"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_rule_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_security_rule" "example" {
                name                       = "test123"
                priority                   = 100
                direction                  = "Inbound"
                access                     = "Deny"
                protocol                   = "Udp"
                source_port_range          = "*"
                destination_port_range     = "*"
                source_address_prefix      = "*"
                destination_address_prefix = "*"
            }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_rule_2(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_network_security_rule" "example" {
            name                       = "test123"
            priority                   = 100
            direction                  = "Outbound"
            access                     = "Allow"
            protocol                   = "Udp"
            source_port_range          = "*"
            destination_port_range     = "*"
            source_address_prefix      = "*"
            destination_address_prefix = "*"
        }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_rule_3(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_network_security_rule" "example" {
            name                       = "test123"
            priority                   = 100
            direction                  = "Inbound"
            access                     = "Allow"
            protocol                   = "Tcp"
            source_port_range          = "*"
            destination_port_range     = "*"
            source_address_prefix      = "*"
            destination_address_prefix = "*"
        }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unsupported_syntax(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_network_security_group" "example" {
          name = "${var.autoscaler_prefix}autoscaler-nsg"
          location = azurerm_resource_group.rg.location
          resource_group_name = azurerm_resource_group.rg.name
        
          security_rule = [for idx, rule in var.autoscaler_ssh_permit: {
            name = "allow-${rule.name}"
            priority = 100 + idx
            direction = "Inbound"
            access = "Allow"
            protocol = "TCP"
            source_address_prefix = rule.ip
            source_port_range = "*"
            destination_address_prefix = "*"
            destination_port_range = "22"
            description = ""
            destination_address_prefixes = null
            destination_application_security_group_ids = null
            destination_port_ranges = null
            source_address_prefixes = null
            source_application_security_group_ids = null
            source_port_ranges = null
          }]
        
          tags = var.autoscaler_tags_nsg
        }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_security_group']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
