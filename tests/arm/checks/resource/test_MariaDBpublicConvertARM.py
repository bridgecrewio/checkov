import unittest
import hcl2
from checkov.arm.checks.resource.MariaDBpublicConvertARM import MariaDBpublicConvertARM, check
from checkov.common.models.enums import CheckResult


class test_MariaDBpublicConvertARM(unittest.TestCase):
    import unittest
    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "azurerm_mariadb_server" "example" {
                name                = var.server_name
                location            = var.resource_group.location
                resource_group_name = var.resource_group.name
                administrator_login          = var.admin_login
                administrator_login_password = random_string.password.result
                sku_name   = "B_Gen5_2"
                storage_mb = 5120
                version    = "10.2"
                auto_grow_enabled             = true
                backup_retention_days         = 7
                geo_redundant_backup_enabled  = false
                public_network_access_enabled = true
                #test this i guess
                ssl_enforcement_enabled = false
            }
                    """)
        resource_conf = hcl_res['resource'][0]['azurerm_mariadb_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mariadb_server" "example" {
                name                = var.server_name
                location            = var.resource_group.location
                resource_group_name = var.resource_group.name
                administrator_login          = var.admin_login
                administrator_login_password = random_string.password.result
                sku_name   = "B_Gen5_2"
                storage_mb = 5120
                version    = "10.2"
                auto_grow_enabled             = true
                backup_retention_days         = 7
                geo_redundant_backup_enabled  = false
                public_network_access_enabled = false
                #test this i guess
                ssl_enforcement_enabled = true
            }
                    """)
        resource_conf = hcl_res['resource'][0]['azurerm_mariadb_server']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    if __name__ == '__main__':
        unittest.main()
