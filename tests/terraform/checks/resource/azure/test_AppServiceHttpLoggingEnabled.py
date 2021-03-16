import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AppServiceHttpLoggingEnabled import check
from checkov.common.models.enums import CheckResult


class TestAppServiceHttpLoggingEnabled(unittest.TestCase):

    def test_failure1(self):
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
              
           logs {
               application_logs {
                   azure_blob_storage {
                   level = "warning"
                   sas_url = "www.example.com"
                   retention_in_days = 4
                }
            }
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

    def test_failure2(self):
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

    def test_success1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
            
              logs {
                http_logs {
                    retention_in_days = 4
                    retention_in_mb = 10
                }
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
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
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
              
               logs {
                   application_logs {
                       azure_blob_storage {
                       level = "warning"
                       sas_url = "www.example.com"
                       retention_in_days = 4
                    }
                }
                    http_logs {
                        retention_in_days = 4
                        retention_in_mb = 10
                    }
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
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
