import unittest

import hcl2

from checkov.terraform.checks.resource.azure.StorageAccountLoggingQueueServiceEnabled import check
from checkov.common.models.enums import CheckResult


class TestStorageAccountLoggingQueueServiceEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              queue_properties  {
                logging {
                }
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              queue_properties  {
                logging {
                  delete                = true
                  read                  = true
                  write                 = true
                  version               = "1.0"
                  retention_policy_days = 10
                }
                hour_metrics {
                  enabled               = true
                  include_apis          = true
                  version               = "1.0"
                  retention_policy_days = 10
                }
                minute_metrics {
                  enabled               = true
                  include_apis          = true
                  version               = "1.0"
                  retention_policy_days = 10
                }
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_blobstorage(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "LRS"
              account_kind             = "BlobStorage"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
