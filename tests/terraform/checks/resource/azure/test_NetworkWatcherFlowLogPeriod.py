import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.NetworkWatcherFlowLogPeriod import check


class TestNetworkWatcherFlowLogPeriod(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
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

                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_network_watcher_flow_log"][
            "test"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
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

                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_network_watcher_flow_log"][
            "test"
        ]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
