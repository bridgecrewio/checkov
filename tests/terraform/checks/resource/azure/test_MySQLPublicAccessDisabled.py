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


if __name__ == '__main__':
    unittest.main()
