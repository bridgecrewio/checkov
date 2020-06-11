import unittest

import hcl2

from checkov.terraform.checks.resource.azure.PostgreSQLServerLogConnectionsEnabled import check
from checkov.common.models.enums import CheckResult


class TestPostgreSQLServerLogConnectionsEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_postgresql_configuration" "example" {
              name                = "log_connections"
              resource_group_name = data.azurerm_resource_group.example.name
              server_name         = azurerm_postgresql_server.example.name
              value               = "off"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_configuration']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_postgresql_configuration" "example" {
              name                = "backslash_quote"
              resource_group_name = azurerm_resource_group.example.name
              server_name         = azurerm_postgresql_server.example.name
              value               = "on"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_configuration']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
