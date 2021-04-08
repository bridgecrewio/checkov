import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AppServiceEnableFailedRequest import check
from checkov.common.models.enums import CheckResult


class TestAppServiceEnableFailedRequest(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              logs {
                failed_request_tracing_enabled = false
                }
              }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
               name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              logs {
                failed_request_tracing_enabled = true
                }
              storage_account {
                name = "test_name"
                type = "AzureFiles"
                account_name ="test_account_name"
                share_name = "test_share_name"
                access_key = "test_access_key"
                }
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failed_missing_failed_request_tracing_enabled_attribute(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              site_config {
                scm_type                 = "someValue"
                }
              logs {
                    application_logs = "test"
                }
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failed_missing_logs_attribute(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              site_config {
                scm_type                 = "someValue"
                }
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
