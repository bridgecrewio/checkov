import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AppServiceJavaVersion import check
from checkov.common.models.enums import CheckResult


class TestAppServiceJavaVersion(unittest.TestCase):

    def test_failure_old_version(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              site_config {
                java_version = "1.7.0_80"
                scm_type                 = "someValue"
                }
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_latest_version(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              https_only          = true
              site_config {
                java_version = "11"
                scm_type                 = "someValue"
                }
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_java(self):
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
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
