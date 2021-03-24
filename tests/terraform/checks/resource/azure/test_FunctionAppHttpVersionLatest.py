import unittest

import hcl2

from checkov.terraform.checks.resource.azure.FunctionAppHttpVersionLatest import check
from checkov.common.models.enums import CheckResult


class TestFunctionAppHttpVersionLatest(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_function_app" "example" {
          name                       = "test-azure-functions"
          location                   = azurerm_resource_group.example.location
          resource_group_name        = azurerm_resource_group.example.name
          app_service_plan_id        = azurerm_app_service_plan.example.id
          storage_account_name       = azurerm_storage_account.example.name
          storage_account_access_key = azurerm_storage_account.example.primary_access_key
          os_type                    = "linux"
        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_function_app']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_function_app" "example" {
          name                       = "test-azure-functions"
          location                   = azurerm_resource_group.example.location
          resource_group_name        = azurerm_resource_group.example.name
          app_service_plan_id        = azurerm_app_service_plan.example.id
          storage_account_name       = azurerm_storage_account.example.name
          storage_account_access_key = azurerm_storage_account.example.primary_access_key
          os_type                    = "linux"
            site_config {
                http2_enabled = false
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_function_app']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_function_app" "example" {
          name                       = "test-azure-functions"
          location                   = azurerm_resource_group.example.location
          resource_group_name        = azurerm_resource_group.example.name
          app_service_plan_id        = azurerm_app_service_plan.example.id
          storage_account_name       = azurerm_storage_account.example.name
          storage_account_access_key = azurerm_storage_account.example.primary_access_key
          os_type                    = "linux"
          site_config {
            http2_enabled = true
          }
        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_function_app']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
