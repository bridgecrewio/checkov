import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SQLServerThreatDetectionTypes import check
from checkov.common.models.enums import CheckResult


class TestSecurityCenterContactPhone(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server_security_alert_policy" "example" {
              resource_group_name        = azurerm_resource_group.example.name
              server_name                = azurerm_sql_server.example.name
              state                      = "Enabled"
              storage_endpoint           = azurerm_storage_account.example.primary_blob_endpoint
              storage_account_access_key = azurerm_storage_account.example.primary_access_key
              disabled_alerts = [
                "Sql_Injection",
                "Data_Exfiltration"
              ]
              retention_days = 20
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server_security_alert_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_mssql_server_security_alert_policy" "example" {
              resource_group_name        = azurerm_resource_group.example.name
              server_name                = azurerm_sql_server.example.name
              state                      = "Enabled"
              storage_endpoint           = azurerm_storage_account.example.primary_blob_endpoint
              storage_account_access_key = azurerm_storage_account.example.primary_access_key
              disabled_alerts = []
              retention_days = 20
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server_security_alert_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
