import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.SQLServerAuditingRetention90Days import (
    check,
)


class TestSQLServerAuditingEnabled(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_sql_server" "example" {
              name                         = "mssqlserver"
              resource_group_name          = azurerm_resource_group.example.name
              location                     = azurerm_resource_group.example.location
              version                      = "12.0"
              administrator_login          = "mradministrator"
              administrator_login_password = "thisIsDog11"
              extended_auditing_policy {
                storage_endpoint                        = azurerm_storage_account.example.primary_blob_endpoint
                storage_account_access_key              = azurerm_storage_account.example.primary_access_key
                storage_account_access_key_is_secondary = true
                retention_in_days                       = 6
              }
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_sql_server"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_sql_server" "example" {
              name                         = "mssqlserver"
              resource_group_name          = azurerm_resource_group.example.name
              location                     = azurerm_resource_group.example.location
              version                      = "12.0"
              administrator_login          = "mradministrator"
              administrator_login_password = "thisIsDog11"

              extended_auditing_policy {
                storage_endpoint                        = azurerm_storage_account.example.primary_blob_endpoint
                storage_account_access_key              = azurerm_storage_account.example.primary_access_key
                storage_account_access_key_is_secondary = true
                retention_in_days                       = 90
              }
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_sql_server"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
