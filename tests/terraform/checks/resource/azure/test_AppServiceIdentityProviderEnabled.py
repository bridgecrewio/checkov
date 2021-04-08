import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AppServiceIdentityProviderEnabled import check
from checkov.common.models.enums import CheckResult


class TestAppServiceIdentityProviderEnabled(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
            
              site_config {
                dotnet_framework_version = "v4.0"
                scm_type                 = "LocalGit"
              }
            
              app_settings = {
                "SOME_KEY" = "some-value"
              }
            
              connection_string {
                name  = "Database"
                type  = "SQLServer"
                value = "Server=some-server.mydomain.com;Integrated Security=SSPI"
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
              site_config {
                dotnet_framework_version = "v5.0"
                scm_type                 = "someValue"
                }
              identity {
                type = "SystemAssigned"
                }
              }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_app_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
