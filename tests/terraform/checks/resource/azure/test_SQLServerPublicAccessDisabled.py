import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SQLServerPublicAccessDisabled import check
from checkov.common.models.enums import CheckResult


class TestSQLServerPublicAccessDisabled(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server" "example" {
              name                         = "mssqlserver"
              resource_group_name          = azurerm_resource_group.example.name
              location                     = azurerm_resource_group.example.location
              version                      = "12.0"
              administrator_login          = "missadministrator"
              administrator_login_password = "thisIsKat11"
              minimum_tls_version          = "1.2"
              public_network_access_enabled = true
              azuread_administrator {
                login_username = "AzureAD Admin"
                object_id      = "00000000-0000-0000-0000-000000000000"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server" "example" {
              name                         = "mssqlserver"
              resource_group_name          = azurerm_resource_group.example.name
              location                     = azurerm_resource_group.example.location
              version                      = "12.0"
              administrator_login          = "missadministrator"
              administrator_login_password = "thisIsKat11"
              minimum_tls_version          = "1.2"
              azuread_administrator {
                login_username = "AzureAD Admin"
                object_id      = "00000000-0000-0000-0000-000000000000"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server" "example" {
              name                         = "mssqlserver"
              resource_group_name          = azurerm_resource_group.example.name
              location                     = azurerm_resource_group.example.location
              version                      = "12.0"
              administrator_login          = "missadministrator"
              administrator_login_password = "thisIsKat11"
              minimum_tls_version          = "1.2"
              public_network_access_enabled = false
              azuread_administrator {
                login_username = "AzureAD Admin"
                object_id      = "00000000-0000-0000-0000-000000000000"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
