import unittest

import hcl2

from checkov.terraform.checks.resource.azure.MonitorLogProfileRetentionDays import check
from checkov.common.models.enums import CheckResult


class TestMonitorLogProfileRetentionDays(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_monitor_log_profile" "example" {
              name = "default"
              categories = [
                "Action",
                "Delete",
                "Write",
              ]
              locations = [
                "westus",
                "global",
              ]
              retention_policy {
                enabled = true
                days    = 7
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_monitor_log_profile']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_monitor_log_profile" "example" {
              name = "default"
              categories = [
                "Action",
                "Delete",
                "Write",
              ]
              locations = [
                "westus",
                "global",
              ]
              retention_policy {
                enabled = true
                days    = null
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_monitor_log_profile']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_1(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_monitor_log_profile" "example" {
              name = "default"
              categories = [
                "Action",
                "Delete",
                "Write",
              ]
              locations = [
                "westus",
                "global",
              ]
              retention_policy {
                enabled = true
                days    = 365
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_monitor_log_profile']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_2(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_monitor_log_profile" "example" {
              name = "default"
              categories = [
                "Action",
                "Delete",
                "Write",
              ]
              locations = [
                "westus",
                "global",
              ]
              retention_policy {
                enabled = false
                days    = 0
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_monitor_log_profile']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_missing(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_monitor_log_profile" "example" {
              name = "default"
              categories = [
                "Action",
                "Delete",
                "Write",
              ]
              locations = [
                "westus",
                "global",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_monitor_log_profile']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_unknown(self):
        hcl_res = hcl2.loads("""
                   resource "azurerm_monitor_log_profile" "example" {
                      name = "default"
                      categories = [
                        "Action",
                        "Delete",
                        "Write",
                      ]
                      locations = [
                        "westus",
                        "global",
                      ]
                      retention_policy {
                        enabled = true
                        days    = var.days
                      }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['azurerm_monitor_log_profile']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)


if __name__ == '__main__':
    unittest.main()
