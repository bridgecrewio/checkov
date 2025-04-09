import unittest

import hcl2

from checkov.terraform.checks.resource.azure.MSSQLServerMinTLSVersion import check
from checkov.common.models.enums import CheckResult


class TestMSSQLServerMinTLSVersion(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server" "examplea" {
              name                          = var.server_name
              resource_group_name           = var.resource_group.name
              location                      = var.resource_group.location
              version                       = var.sql["version"]
              administrator_login           = var.sql["administrator_login"]
              administrator_login_password  = local.administrator_login_password
              minimum_tls_version           = "1.1"
              public_network_access_enabled = var.sql["public_network_access_enabled"]
              identity {
                type = "SystemAssigned"
              }
              tags = var.common_tags
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server" "examplea" {
              name                          = var.server_name
              resource_group_name           = var.resource_group.name
              location                      = var.resource_group.location
              version                       = var.sql["version"]
              administrator_login           = var.sql["administrator_login"]
              administrator_login_password  = local.administrator_login_password
              minimum_tls_version           = "1.2"
              public_network_access_enabled = var.sql["public_network_access_enabled"]
              identity {
                type = "SystemAssigned"
              }
              tags = var.common_tags
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
