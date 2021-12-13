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
                  file_system {
                    retention_in_days = 4
                    retention_in_mb = 10
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
                  file_system {
                    retention_in_days = 4
                    retention_in_mb = 10
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
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success3(self):
        hcl_res = hcl2.loads("""
            variable "enable_http_logs" {
              type = bool
              default = true
            }

            variable "enable_http_logs_file_system" {
              type = bool
              default = true
            }

            variable "http_logs_azure_blob_storage" {
              type = bool
              default = true
            }

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

                dynamic "http_logs" {
                  for_each = var.enable_http_logs ? [1] : []

                  content {
                    dynamic "file_system" {
                      for_each = var.enable_http_logs_file_system ? [1] : []

                      content {
                        retention_in_days = 4
                        retention_in_mb = 10
                      }
                    }

                    dynamic "azure_blob_storage" {
                      for_each = var.http_logs_azure_blob_storage != null ? [1] : []
                      content {
                        retention_in_days = 10
                        sas_url           = "https://something.com"
                      }
                    }
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
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
