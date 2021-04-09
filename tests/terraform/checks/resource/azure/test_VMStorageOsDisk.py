import unittest

import hcl2

from checkov.terraform.checks.resource.azure.VMStorageOsDisk import check
from checkov.common.models.enums import CheckResult


class TestVMStorageOsDisk(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
                            resource "azurerm_windows_virtual_machine" "example" {
                              name                  = "${var.prefix}-vm"
                              location              = azurerm_resource_group.main.location
                              resource_group_name   = azurerm_resource_group.main.name
                              network_interface_ids = [azurerm_network_interface.main.id]
                              vm_size               = "Standard_DS1_v2"
                            
                              storage_image_reference {
                                publisher = "Canonical"
                                offer     = "UbuntuServer"
                                sku       = "16.04-LTS"
                                version   = "latest"
                              }
                              storage_os_disk {
                                name              = "myosdisk1"
                                caching           = "ReadWrite"
                                create_option     = "FromImage"
                                managed_disk_type = "Standard_LRS"
                              }
                              os_profile {
                                computer_name  = "hostname"
                                admin_username = "testadmin"
                                admin_password = "Password1234!"
                              }
                              tags = {
                                environment = "staging"
                              }
                            }    
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_windows_virtual_machine']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_param(self):
        hcl_res = hcl2.loads("""
                            resource "azurerm_linux_virtual_machine" "example" {
                              name                  = "${var.prefix}-vm"
                              location              = azurerm_resource_group.main.location
                              resource_group_name   = azurerm_resource_group.main.name
                              network_interface_ids = [azurerm_network_interface.main.id]
                              vm_size               = "Standard_DS1_v2"
                            
                              storage_image_reference {
                                publisher = "Canonical"
                                offer     = "UbuntuServer"
                                sku       = "16.04-LTS"
                                version   = "latest"
                              }
                              os_profile {
                                computer_name  = "hostname"
                                admin_username = "testadmin"
                                admin_password = "Password1234!"
                              }
                              tags = {
                                environment = "staging"
                              }
                            }    
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
                            resource "azurerm_linux_virtual_machine" "example" {
                              name                  = "${var.prefix}-vm"
                              location              = azurerm_resource_group.main.location
                              resource_group_name   = azurerm_resource_group.main.name
                              network_interface_ids = [azurerm_network_interface.main.id]
                              vm_size               = "Standard_DS1_v2"
                            
                              storage_image_reference {
                                publisher = "Canonical"
                                offer     = "UbuntuServer"
                                sku       = "16.04-LTS"
                                version   = "latest"
                              }
                              storage_os_disk {
                                name              = "myosdisk1"
                                caching           = "ReadWrite"
                                create_option     = "FromImage"
                                managed_disk_type = "Standard_LRS"
                                vhd_uri           = "someURI"
                              }
                              os_profile {
                                computer_name  = "hostname"
                                admin_username = "testadmin"
                                admin_password = "Password1234!"
                              }
                              tags = {
                                environment = "staging"
                              }
                            }    
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
                            resource "azurerm_windows_virtual_machine" "example" {
                              name                  = "${var.prefix}-vm"
                              location              = azurerm_resource_group.main.location
                              resource_group_name   = azurerm_resource_group.main.name
                              network_interface_ids = [azurerm_network_interface.main.id]
                              vm_size               = "Standard_DS1_v2"
                            
                              storage_image_reference {
                                publisher = "Canonical"
                                offer     = "UbuntuServer"
                                sku       = "16.04-LTS"
                                version   = "latest"
                              }
                              storage_data_disk {
                                name              = "myosdisk1"
                                caching           = "ReadWrite"
                                create_option     = "FromImage"
                                managed_disk_type = "Standard_LRS"
                                vhd_uri           = "someURI"
                              }
                              os_profile {
                                computer_name  = "hostname"
                                admin_username = "testadmin"
                                admin_password = "Password1234!"
                              }
                              tags = {
                                environment = "staging"
                              }
                            }    
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_windows_virtual_machine']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
