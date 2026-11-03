import unittest
from pathlib import Path

import hcl2
import pytest

from checkov.terraform.checks.resource.azure.SQLServerEmailAlertsToAdminsEnabled import check
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


@pytest.mark.parametrize("attributes,expected,key", [
    ('email_account_admins_enabled = true', CheckResult.PASSED, 'email_account_admins_enabled'),
    ('email_account_admins_enabled = false', CheckResult.FAILED, 'email_account_admins_enabled'),
    ('email_account_admins_enabled = null', CheckResult.FAILED, 'email_account_admins_enabled'),
    ('email_account_admins_enabled = var.admin_alerts', CheckResult.UNKNOWN, 'email_account_admins_enabled'),
    ('email_account_admins = true', CheckResult.PASSED, 'email_account_admins'),
    ('email_account_admins = false', CheckResult.FAILED, 'email_account_admins'),
    ('email_account_admins = var.admin_alerts', CheckResult.UNKNOWN, 'email_account_admins'),
    ('', CheckResult.FAILED, 'email_account_admins'),
    ('email_account_admins_enabled = false\nemail_account_admins = true',
     CheckResult.FAILED, 'email_account_admins_enabled'),
    ('email_account_admins_enabled = true\nemail_account_admins = false',
     CheckResult.PASSED, 'email_account_admins_enabled'),
])
def test_admin_email_attributes(attributes, expected, key):
    resource = hcl2.loads('''
        resource "azurerm_mssql_server_security_alert_policy" "example" {
            state = "Enabled"
            %s
        }
    ''' % attributes)['resource'][0]['azurerm_mssql_server_security_alert_policy']['example']

    assert check.scan_resource_conf(resource) == expected
    assert check.get_evaluated_keys() == [key]


def test_module_inputs():
    test_dir = Path(__file__).parent / 'example_SQLServerEmailAlertsToAdminsEnabled'
    report = Runner().run(root_folder=str(test_dir), runner_filter=RunnerFilter(checks=[check.id]))

    assert {record.resource for record in report.passed_checks} == {
        'module.enabled.azurerm_mssql_server_security_alert_policy.example',
    }
    assert {record.resource for record in report.failed_checks} == {
        'module.disabled.azurerm_mssql_server_security_alert_policy.example',
    }
    assert report.get_summary()['skipped'] == 0
    assert report.get_summary()['parsing_errors'] == 0
    for record in report.passed_checks + report.failed_checks:
        assert record.check_result['evaluated_keys'] == ['email_account_admins_enabled']


class TestSQLServerEmailAlertsToAdminsEnabled(unittest.TestCase):

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
              email_addresses = ["example@gmail.com"]
              email_account_admins = true
              retention_days = 20
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_mssql_server_security_alert_policy']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
