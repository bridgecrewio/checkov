import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SQLServerNoPublicAccess import check
from checkov.common.models.enums import CheckResult


class TestSQLServerNoPublicAccess(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mysql_firewall_rule" "example" {
              name                = "office"
              resource_group_name = azurerm_resource_group.example.name
              server_name         = azurerm_mysql_server.example.name
              start_ip_address    = "0.0.0.0"
              end_ip_address      = "255.255.255.255"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_firewall_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_allow_azure_services(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mysql_firewall_rule" "example" {
              name                = "office"
              resource_group_name = azurerm_resource_group.example.name
              server_name         = azurerm_mysql_server.example.name
              start_ip_address    = "0.0.0.0"
              end_ip_address      = "0.0.0.0"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_firewall_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mysql_firewall_rule" "example" {
              name                = "office"
              resource_group_name = azurerm_resource_group.example.name
              server_name         = azurerm_mysql_server.example.name
              start_ip_address    = "40.112.8.12"
              end_ip_address      = "40.112.8.17"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_firewall_rule']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
