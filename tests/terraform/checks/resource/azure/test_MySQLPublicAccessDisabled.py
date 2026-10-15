import unittest

import hcl2

from checkov.terraform.checks.resource.azure.MySQLPublicAccessDisabled import check
from checkov.common.models.enums import CheckResult


class TestMySQLPublicAccessDisabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mysql_server" "examplea" {
  name                = var.mysqlserver_name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name

  administrator_login          = var.admin_name
  administrator_login_password = var.password
  sku_name = var.sku_name
  storage_mb = var.storage_mb
  version    = var.server_version

  auto_grow_enabled            = true
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  infrastructure_encryption_enabled = false
    public_network_access_enabled = true
}
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_server']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_missing_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mysql_server" "examplea" {
  name                = var.mysqlserver_name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name

  administrator_login          = var.admin_name
  administrator_login_password = var.password
  sku_name = var.sku_name
  storage_mb = var.storage_mb
  version    = var.server_version

  auto_grow_enabled            = true
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  infrastructure_encryption_enabled = false
}
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_server']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "azurerm_mysql_server" "examplea" {
  name                = var.mysqlserver_name
  location            = var.resource_group.location
  resource_group_name = var.resource_group.name

  administrator_login          = var.admin_name
  administrator_login_password = var.password
  sku_name = var.sku_name
  storage_mb = var.storage_mb
  version    = var.server_version

  auto_grow_enabled            = true
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  infrastructure_encryption_enabled = false
  public_network_access_enabled = false
}
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_server']['examplea']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def _scan_flexible_server(self, body):
        hcl_res = hcl2.loads(f"""
resource "azurerm_mysql_flexible_server" "examplea" {{
  name                   = var.mysqlserver_name
  location               = var.resource_group.location
  resource_group_name    = var.resource_group.name
  administrator_login    = var.admin_name
  administrator_password = var.password
  sku_name               = var.sku_name
  version                = var.server_version
{body}
}}
""")
        resource_conf = hcl_res['resource'][0]['azurerm_mysql_flexible_server']['examplea']
        # `public_network_access_enabled` is computed on a flexible server; the
        # check reads `public_network_access` and VNet integration instead
        check.entity_type = "azurerm_mysql_flexible_server"
        try:
            return check.scan_resource_conf(conf=resource_conf)
        finally:
            check.entity_type = ""

    def test_flexible_server_supported(self):
        self.assertIn("azurerm_mysql_flexible_server", check.supported_resources)

    def test_flexible_server_public_access_enabled_failure(self):
        self.assertEqual(CheckResult.FAILED, self._scan_flexible_server('public_network_access = "Enabled"'))

    def test_flexible_server_missing_failure(self):
        self.assertEqual(CheckResult.FAILED, self._scan_flexible_server(""))

    def test_flexible_server_public_access_disabled_success(self):
        self.assertEqual(CheckResult.PASSED, self._scan_flexible_server('public_network_access = "Disabled"'))

    def test_flexible_server_vnet_integration_success(self):
        body = """
  delegated_subnet_id = azurerm_subnet.example.id
  private_dns_zone_id = azurerm_private_dns_zone.example.id
"""
        self.assertEqual(CheckResult.PASSED, self._scan_flexible_server(body))

    def test_flexible_server_variable_unknown(self):
        self.assertEqual(CheckResult.UNKNOWN, self._scan_flexible_server("public_network_access = var.public_access"))

if __name__ == '__main__':
    unittest.main()
