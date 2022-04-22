import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SQLServerAdminLoginPasswordNotHardCoded import check
from checkov.common.models.enums import CheckResult


class TestSQLServerAdminLoginPasswordNotHardCoded(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_sql_server" "sql_server" {
              provider                     = azurerm.providername
              name                         = var.sql_server_name
              resource_group_name          = azurerm_resource_group.sql_rg.name
              location                     = var.location
              version                      = "12.0"
              administrator_login          = "adminuser"
              administrator_login_password = "My_STRONG_password(!)"
              tags                         = var.tags
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_sql_server']['sql_server']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_postgresql_flexible_server" "psql" {
                name                   = "${var.postgresql_name}"
                resource_group_name    = azurerm_resource_group.postrgressql_rg.name
                location               = azurerm_resource_group.postrgressql_rg.location
                version                = "13"
                delegated_subnet_id    = var.delegated_subnet_id
                private_dns_zone_id    = azurerm_private_dns_zone.private_dns.id
                administrator_login    = "psqladmin"
                administrator_password = "My_STRONG_password(!)"
                zone                   = "1"

                sku_name   = "B_Standard_B1ms"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_flexible_server']['psql']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_sql_server" "sql_server" {
                provider                     = azurerm.providername
                name                         = "${var.sql_server_name}"
                resource_group_name          = azurerm_resource_group.sql_rg.name
                location                     = var.location
                version                      = "12.0"
                administrator_login          = "adminuser"
                administrator_login_password = data.azurerm_key_vault_secret.sql_password.value
                tags                         = var.tags
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_sql_server']['sql_server']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
            variable "sql_password" {
                description = "Admin password needs to be passed in."
                type        = string
            }

            resource "azurerm_postgresql_flexible_server" "psql" {
            name                   = "${var.postgresql_name}"
            resource_group_name    = azurerm_resource_group.postrgressql_rg.name
            location               = azurerm_resource_group.postrgressql_rg.location
            version                = "13"
            delegated_subnet_id    = var.delegated_subnet_id
            private_dns_zone_id    = azurerm_private_dns_zone.private_dns.id
            administrator_login    = "psqladmin"
            administrator_password = var.sql_password
            zone                   = "1"

            sku_name   = "B_Standard_B1ms"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_flexible_server']['psql']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
