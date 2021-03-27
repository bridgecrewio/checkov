import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AzureInstanceExtensions import check


class TestAzureInstanceExtensions(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_linux_virtual_machine" "example" {
              name                = "example-machine"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              size                = "Standard_F2"
              admin_username      = "adminuser"
              allow_extension_operations=true
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_linux_virtual_machine"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_linux_virtual_machine" "example" {
              name                = "example-machine"
              resource_group_name = azurerm_resource_group.example.name
              location            = azurerm_resource_group.example.location
              size                = "Standard_F2"
              admin_username      = "adminuser"
              allow_extension_operations=false
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_linux_virtual_machine"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_winfailure(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_windows_virtual_machine" "example" {
              name                       = "example-machine"
              resource_group_name        = azurerm_resource_group.example.name
              location                   = azurerm_resource_group.example.location
              size                       = "Standard_F2"
              admin_username             = "adminuser"
              admin_password             = "P@$$w0rd1234!"
              allow_extension_operations = true
              network_interface_ids = [
                azurerm_network_interface.example.id,
                ]
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_windows_virtual_machine"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_winsuccess(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_windows_virtual_machine" "example" {
              name                       = "example-machine"
              resource_group_name        = azurerm_resource_group.example.name
              location                   = azurerm_resource_group.example.location
              size                       = "Standard_F2"
              admin_username             = "adminuser"
              admin_password             = "P@$$w0rd1234!"
              network_interface_ids = [
                azurerm_network_interface.example.id,
                ]
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_windows_virtual_machine"][
            "example"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
