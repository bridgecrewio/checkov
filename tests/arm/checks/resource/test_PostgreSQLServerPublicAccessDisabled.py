import unittest
from checkov.arm.checks.resource.PostgreSQLServerPublicAccessDisabled import check
from checkov.common.models.enums import CheckResult


class TestPostgreSQLServerPublicAccessDisabled(unittest.TestCase):

    def test_failure_1(self):
        resource_conf = {
            "type": "Microsoft.DBforPostgreSQL/servers",
            "apiVersion": "2021-02-01",
            "name": "example-psqlserver",
            "location": "[azurerm_resource_group.example.location]",
            "sku": {
                "name": "GP_Gen5_4"
            },
            "properties": {
                "administrator_login": "psqladminun",
                "administrator_login_password": "H@Sh1CoR3!",  # checkov:skip=CKV_SECRET_80 test secret
                "version": "9.6",
                "storageProfile": {
                    "storageMB": 640000,
                    "backupRetentionDays": 7,
                    "geoRedundantBackup": "Enabled",
                    "auto_grow_enabled": "Enabled"
                },
                "publicNetworkAccess": "Enabled",
                "ssl_enforcement_enabled ": True,
                "ssl_minimal_tls_version_enforced": "TLS1_2"
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        resource_conf = {
            "type": "Microsoft.DBforPostgreSQL/servers",
            "apiVersion": "2021-02-01",
            "name": "example-psqlserver",
            "location": "azurerm_resource_group.example.location",
            "sku": {
                "name": "GP_Gen5_4"
            },
            "properties": {
                "administrator_login": "psqladminun",
                "administrator_login_password": "H@Sh1CoR3!",
                "version": "9.6",
                "storageProfile": {
                    "storageMB": 640000,
                    "backupRetentionDays": 7,
                    "geoRedundantBackup": "Enabled",
                    "auto_grow_enabled": "Enabled"
                },
                "ssl_enforcement_enabled ": True,
                "ssl_minimal_tls_version_enforced": "TLS1_2"
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "type": "Microsoft.DBforPostgreSQL/servers",
            "apiVersion": "2021-02-01",
            "name": "example-psqlserver",
            "location": "[azurerm_resource_group.example.location]",
            "properties": {
                "administrator_login": "psqladminun",
                "administrator_login_password": "H@Sh1CoR3!",
                "version": "9.6",
                "storageProfile": {
                    "storageMB": 640000,
                    "backupRetentionDays": 7,
                    "geoRedundantBackup": "Enabled",
                    "auto_grow_enabled": "Enabled"
                },
                "publicNetworkAccess": "Disabled",
                "ssl_enforcement_enabled ": True,
                "ssl_minimal_tls_version_enforced": "TLS1_2"
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
