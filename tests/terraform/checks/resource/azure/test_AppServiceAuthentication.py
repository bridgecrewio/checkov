import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AppServiceAuthentication import check


class TestAppServiceAuthentication(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id
              }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_app_service"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_app_service" "example" {
              name                = "example-app-service"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              app_service_plan_id = azurerm_app_service_plan.example.id

              auth_settings {
                enabled                       = true
                issuer                        = "https://sts.windows.net/d13958f6-b541-4dad-97b9-5a39c6b01297"
                default_provider              = "AzureActiveDirectory"
                unauthenticated_client_action = "RedirectToLoginPage"
            }
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_app_service"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
