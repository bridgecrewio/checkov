import unittest

import hcl2

from checkov.terraform.checks.resource.azure.NetworkInterfacePublicIPAddressId import check
from checkov.common.models.enums import CheckResult


class TestNetworkInterfacePublicIPAddressId(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_network_interface" "example" {
                  name                = "example-nic"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                
                  ip_configuration {
                    name                          = "internal"
                    subnet_id                     = azurerm_subnet.example.id
                    private_ip_address_allocation = "Dynamic"
                  }       
                    ip_configuration {
                    name                          = "internal2"
                    subnet_id                     = azurerm_subnet.example.id2
                    private_ip_address_allocation = "Dynamic"
                    public_ip_address_id          = azurerm_subnet.example2.id
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_interface']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_network_interface" "example" {
                  name                = "example-nic"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                
                  ip_configuration {
                    name                          = "internal"
                    subnet_id                     = azurerm_subnet.example.id
                    private_ip_address_allocation = "Dynamic"
                  }       
                    ip_configuration {
                    name                          = "internal2"
                    subnet_id                     = azurerm_subnet.example.id2
                    private_ip_address_allocation = "Dynamic"
                  }
                  enable_ip_forwarding = false
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_interface']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_with_null(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_network_interface" "example" {
                  name                = "example-nic"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                
                  ip_configuration {
                    name                          = "internal"
                    subnet_id                     = azurerm_subnet.example.id
                    private_ip_address_allocation = "Dynamic"
                    public_ip_address_id = null
                  }       
                    ip_configuration {
                    name                          = "internal2"
                    subnet_id                     = azurerm_subnet.example.id2
                    private_ip_address_allocation = "Dynamic"
                    public_ip_address_id = null
                  }
                  enable_ip_forwarding = false
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_interface']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_param(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_network_interface" "example" {
                  name                = "example-nic"
                  location            = azurerm_resource_group.example.location
                  resource_group_name = azurerm_resource_group.example.name
                
                }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_interface']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
