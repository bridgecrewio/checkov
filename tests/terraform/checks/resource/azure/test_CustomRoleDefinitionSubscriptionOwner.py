import unittest

import hcl2

from checkov.terraform.checks.resource.azure.CutsomRoleDefinitionSubscriptionOwner import check
from checkov.common.models.enums import CheckResult


class TestCustomRoleDefinitionSubscriptionOwner(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_role_definition" "example" {
              name        = "my-custom-role"
              scope       = data.azurerm_subscription.primary.id
              description = "This is a custom role created via Terraform"
            
              permissions {
                actions     = ["*"]
                not_actions = []
              }
            
              assignable_scopes = [
                data.azurerm_subscription.primary.id
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_role_definition']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_role_definition" "example" {
              name        = "my-custom-role"
              scope       = data.azurerm_subscription.primary.id
              description = "This is a custom role created via Terraform"

              permissions {
                actions     = ["*"]
                not_actions = []
              }

              assignable_scopes = [
                "/"
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_role_definition']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_role_definition" "example" {
              name        = "my-custom-role"
              scope       = data.azurerm_subscription.primary.id
              description = "This is a custom role created via Terraform"
            
              permissions {
                actions     = [
                "Microsoft.Authorization/*/read",
                  "Microsoft.Insights/alertRules/*",
                  "Microsoft.Resources/deployments/write",
                  "Microsoft.Resources/subscriptions/operationresults/read",
                  "Microsoft.Resources/subscriptions/read",
                  "Microsoft.Resources/subscriptions/resourceGroups/read",
                  "Microsoft.Support/*"
                  ]
                not_actions = []
              }
            
              assignable_scopes = [
                data.azurerm_subscription.primary.id
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_role_definition']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_no_assignable_scopes(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_role_definition" "example" {
              name        = "my-custom-role"
              scope       = data.azurerm_subscription.primary.id
              description = "This is a custom role created via Terraform"

              permissions {
                actions     = ["*"]
                not_actions = []
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_role_definition']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
