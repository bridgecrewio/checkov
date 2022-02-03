import unittest

import hcl2

from checkov.terraform.checks.resource.azure.PostgreSQLFlexiServerGeoBackupEnabled import check
from checkov.common.models.enums import CheckResult


class TestPostgreSQLFlexiServerGeoBackupEnabled(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_postgresql_flexible_server" "example" {
              name                   = "example-psqlflexibleserver"
              resource_group_name    = azurerm_resource_group.example.name
              location               = azurerm_resource_group.example.location
              version                = "12"
              delegated_subnet_id    = azurerm_subnet.example.id
              private_dns_zone_id    = azurerm_private_dns_zone.example.id
              administrator_login    = "psqladmin"
              administrator_password = "H@Sh1CoR3!"
              zone                   = "1"
            
              storage_mb = 32768
              geo_redundant_backup_enabled = false
            
              sku_name   = "GP_Standard_D4s_v3"
              depends_on = [azurerm_private_dns_zone_virtual_network_link.example]
            
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_flexible_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_postgresql_flexible_server" "example" {
              name                   = "example-psqlflexibleserver"
              resource_group_name    = azurerm_resource_group.example.name
              location               = azurerm_resource_group.example.location
              version                = "12"
              delegated_subnet_id    = azurerm_subnet.example.id
              private_dns_zone_id    = azurerm_private_dns_zone.example.id
              administrator_login    = "psqladmin"
              administrator_password = "H@Sh1CoR3!"
              zone                   = "1"
            
              storage_mb = 32768
            
              sku_name   = "GP_Standard_D4s_v3"
              depends_on = [azurerm_private_dns_zone_virtual_network_link.example]
            
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_flexible_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_postgresql_flexible_server" "example" {
              name                   = "example-psqlflexibleserver"
              resource_group_name    = azurerm_resource_group.example.name
              location               = azurerm_resource_group.example.location
              version                = "12"
              delegated_subnet_id    = azurerm_subnet.example.id
              private_dns_zone_id    = azurerm_private_dns_zone.example.id
              administrator_login    = "psqladmin"
              administrator_password = "H@Sh1CoR3!"
              zone                   = "1"
            
              storage_mb = 32768
              geo_redundant_backup_enabled = true
            
              sku_name   = "GP_Standard_D4s_v3"
              depends_on = [azurerm_private_dns_zone_virtual_network_link.example]
            
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_postgresql_flexible_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
