import unittest

import hcl2

from checkov.arm.checks.resource.FunctionAppsEnableAuthentication import check
from checkov.common.models.enums import CheckResult


class TestFunctionAppsEnableAuthentication(unittest.TestCase):

    def test_failure_missing_authentication_block(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_function_app" "example" {
              name                       = "test-azure-functions"
              location                   = "azurerm_resource_group.example.location"
              resource_group_name        = "azurerm_resource_group.example.name"
              app_service_plan_id        = "azurerm_app_service_plan.example.id"
              storage_account_name       = "azurerm_storage_account.example.name"
              storage_account_access_key = "azurerm_storage_account.example.primary_access_key"
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_function_app']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_function_app" "example" {
              name                       = "test-azure-functions"
              location                   = "azurerm_resource_group.example.location"
              resource_group_name        = "azurerm_resource_group.example.name"
              app_service_plan_id        = "azurerm_app_service_plan.example.id"
              storage_account_name       = "azurerm_storage_account.example.name"
              storage_account_access_key = "azurerm_storage_account.example.primary_access_key"
              auth_settings {
                enabled = true
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_function_app']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failed(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_function_app" "example" {
              name                       = "test-azure-functions"
              location                   = "azurerm_resource_group.example.location"
              resource_group_name        = "azurerm_resource_group.example.name"
              app_service_plan_id        = "azurerm_app_service_plan.example.id"
              storage_account_name       = "azurerm_storage_account.example.name"
              storage_account_access_key = "azurerm_storage_account.example.primary_access_key"
              auth_settings {
                enabled = false
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_function_app']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
