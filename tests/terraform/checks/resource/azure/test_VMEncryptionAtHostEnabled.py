import unittest

import hcl2

from checkov.terraform.checks.resource.azure.VMEncryptionAtHostEnabled import check
from checkov.common.models.enums import CheckResult


class TestVMEncryptionAtHostEnabled(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
             resource "azurerm_windows_virtual_machine_scale_set" "example" {
                  name                = "example-vmss"
                  resource_group_name = azurerm_resource_group.example.name
                  location            = azurerm_resource_group.example.location
                  sku                 = "Standard_F2"
                  instances           = 1
                  admin_password      = "P@55w0rd1234!"  # checkov:skip=CKV_SECRET_80 test secret
                  admin_username      = "adminuser"
                
                  source_image_reference {
                    publisher = "MicrosoftWindowsServer"
                    offer     = "WindowsServer"
                    sku       = "2016-Datacenter-Server-Core"
                    version   = "latest"
                  }
                
                  os_disk {
                    storage_account_type = "Standard_LRS"
                    caching              = "ReadWrite"
                  }
                
                  network_interface {
                    name    = "example"
                    primary = true
                
                    ip_configuration {
                      name      = "internal"
                      primary   = true
                      subnet_id = azurerm_subnet.internal.id
                    }
                  }
                }   """)
        resource_conf = hcl_res['resource'][0]['azurerm_windows_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
             resource "azurerm_windows_virtual_machine_scale_set" "example" {
                  name                = "example-vmss"
                  resource_group_name = azurerm_resource_group.example.name
                  location            = azurerm_resource_group.example.location
                  sku                 = "Standard_F2"
                  instances           = 1
                  admin_password      = "P@55w0rd1234!"
                  admin_username      = "adminuser"
                  encryption_at_host_enabled = false

                  source_image_reference {
                    publisher = "MicrosoftWindowsServer"
                    offer     = "WindowsServer"
                    sku       = "2016-Datacenter-Server-Core"
                    version   = "latest"
                  }

                  os_disk {
                    storage_account_type = "Standard_LRS"
                    caching              = "ReadWrite"
                  }

                  network_interface {
                    name    = "example"
                    primary = true

                    ip_configuration {
                      name      = "internal"
                      primary   = true
                      subnet_id = azurerm_subnet.internal.id
                    }
                  }
                }   """)
        resource_conf = hcl_res['resource'][0]['azurerm_windows_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure3(self):
        hcl_res = hcl2.loads("""
             resource "azurerm_linux_virtual_machine_scale_set" "example" {
                  name                = "example-vmss"
                  resource_group_name = azurerm_resource_group.example.name
                  location            = azurerm_resource_group.example.location
                  sku                 = "Standard_F2"
                  instances           = 1
                  admin_password      = "P@55w0rd1234!"
                  admin_username      = "adminuser"

                  source_image_reference {
                    publisher = "MicrosoftWindowsServer"
                    offer     = "WindowsServer"
                    sku       = "2016-Datacenter-Server-Core"
                    version   = "latest"
                  }

                  os_disk {
                    storage_account_type = "Standard_LRS"
                    caching              = "ReadWrite"
                  }

                  network_interface {
                    name    = "example"
                    primary = true

                    ip_configuration {
                      name      = "internal"
                      primary   = true
                      subnet_id = azurerm_subnet.internal.id
                    }
                  }
                }   """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure4(self):
        hcl_res = hcl2.loads("""
             resource "azurerm_linux_virtual_machine_scale_set" "example" {
                  name                = "example-vmss"
                  resource_group_name = azurerm_resource_group.example.name
                  location            = azurerm_resource_group.example.location
                  sku                 = "Standard_F2"
                  instances           = 1
                  admin_password      = "P@55w0rd1234!"
                  admin_username      = "adminuser"
                  encryption_at_host_enabled = false

                  source_image_reference {
                    publisher = "MicrosoftWindowsServer"
                    offer     = "WindowsServer"
                    sku       = "2016-Datacenter-Server-Core"
                    version   = "latest"
                  }

                  os_disk {
                    storage_account_type = "Standard_LRS"
                    caching              = "ReadWrite"
                  }

                  network_interface {
                    name    = "example"
                    primary = true

                    ip_configuration {
                      name      = "internal"
                      primary   = true
                      subnet_id = azurerm_subnet.internal.id
                    }
                  }
                }   """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success1(self):
        hcl_res = hcl2.loads("""
             resource "azurerm_windows_virtual_machine_scale_set" "example" {
                  name                = "example-vmss"
                  resource_group_name = azurerm_resource_group.example.name
                  location            = azurerm_resource_group.example.location
                  sku                 = "Standard_F2"
                  instances           = 1
                  admin_password      = "P@55w0rd1234!"
                  admin_username      = "adminuser"
                  encryption_at_host_enabled = true

                  source_image_reference {
                    publisher = "MicrosoftWindowsServer"
                    offer     = "WindowsServer"
                    sku       = "2016-Datacenter-Server-Core"
                    version   = "latest"
                  }

                  os_disk {
                    storage_account_type = "Standard_LRS"
                    caching              = "ReadWrite"
                  }

                  network_interface {
                    name    = "example"
                    primary = true

                    ip_configuration {
                      name      = "internal"
                      primary   = true
                      subnet_id = azurerm_subnet.internal.id
                    }
                  }
                }   """)
        resource_conf = hcl_res['resource'][0]['azurerm_windows_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
             resource "azurerm_linux_virtual_machine_scale_set" "example" {
                  name                = "example-vmss"
                  resource_group_name = azurerm_resource_group.example.name
                  location            = azurerm_resource_group.example.location
                  sku                 = "Standard_F2"
                  instances           = 1
                  admin_password      = "P@55w0rd1234!"
                  admin_username      = "adminuser"
                  encryption_at_host_enabled = true

                  source_image_reference {
                    publisher = "MicrosoftWindowsServer"
                    offer     = "WindowsServer"
                    sku       = "2016-Datacenter-Server-Core"
                    version   = "latest"
                  }

                  os_disk {
                    storage_account_type = "Standard_LRS"
                    caching              = "ReadWrite"
                  }

                  network_interface {
                    name    = "example"
                    primary = true

                    ip_configuration {
                      name      = "internal"
                      primary   = true
                      subnet_id = azurerm_subnet.internal.id
                    }
                  }
                }   """)
        resource_conf = hcl_res['resource'][0]['azurerm_linux_virtual_machine_scale_set']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
