import unittest

import hcl2

from checkov.terraform.checks.resource.azure.NetworkWatcherFlowLogPeriod import check
from checkov.common.models.enums import CheckResult


class TestNetworkWatcherFlowLogPeriod(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_watcher_flow_log" "test" {
              network_watcher_name = azurerm_network_watcher.test.name
              resource_group_name  = azurerm_resource_group.test.name
              network_security_group_id = azurerm_network_security_group.test.id
              storage_account_id        = azurerm_storage_account.test.id
              enabled                   = true
            
              retention_policy {
                enabled = true
                days    = 7
              }
              }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_watcher_flow_log']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_retention_policy(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_watcher_flow_log" "test" {
              network_watcher_name = azurerm_network_watcher.test.name
              resource_group_name  = azurerm_resource_group.test.name
              network_security_group_id = azurerm_network_security_group.test.id
              storage_account_id        = azurerm_storage_account.test.id
              enabled                   = true
            }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_watcher_flow_log']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_invalid_days_string(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_watcher_flow_log" "test" {
              network_watcher_name = azurerm_network_watcher.test.name
              resource_group_name  = azurerm_resource_group.test.name
              network_security_group_id = azurerm_network_security_group.test.id
              storage_account_id        = azurerm_storage_account.test.id
              enabled                   = true
            
              retention_policy {
                enabled = true
                days = var.watcher_flow_logs.days
              }
              }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_watcher_flow_log']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_watcher_flow_log" "test" {
              network_watcher_name = azurerm_network_watcher.test.name
              resource_group_name  = azurerm_resource_group.test.name
              network_security_group_id = azurerm_network_security_group.test.id
              storage_account_id        = azurerm_storage_account.test.id
              enabled                   = true
            
              retention_policy {
                enabled = true
                days    = 90
              }
              }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_watcher_flow_log']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_with_0_days(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_watcher_flow_log" "test" {
              network_watcher_name = azurerm_network_watcher.test.name
              resource_group_name  = azurerm_resource_group.test.name
              network_security_group_id = azurerm_network_security_group.test.id
              storage_account_id        = azurerm_storage_account.test.id
              enabled                   = true
            
              retention_policy {
                enabled = true
                days    = 0
              }
              }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_watcher_flow_log']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_with_valid_day_string(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_network_watcher_flow_log" "test" {
              network_watcher_name = azurerm_network_watcher.test.name
              resource_group_name  = azurerm_resource_group.test.name
              network_security_group_id = azurerm_network_security_group.test.id
              storage_account_id        = azurerm_storage_account.test.id
              enabled                   = true
            
              retention_policy {
                enabled = true
                days    = "100"
              }
              }

                """)
        resource_conf = hcl_res['resource'][0]['azurerm_network_watcher_flow_log']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
