import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AutomationEncrypted import check
from checkov.common.models.enums import CheckResult


class TestAutomationEncrypted(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                        resource "azurerm_automation_variable_string" "example" {
                          name                    = "tfex-example-var"
                          resource_group_name     = azurerm_resource_group.example.name
                          automation_account_name = azurerm_automation_account.example.name
                          value                   = "Hello, Terraform Basic Test."
                          encrypted               = false
                        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_automation_variable_string']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_param(self):
        hcl_res = hcl2.loads("""
                        resource "azurerm_automation_variable_datetime" "example" {
                          name                    = "tfex-example-var"
                          resource_group_name     = azurerm_resource_group.example.name
                          automation_account_name = azurerm_automation_account.example.name
                          value                   = "Hello, Terraform Basic Test."
                        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_automation_variable_datetime']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                        resource "azurerm_automation_variable_int" "example" {
                          name                    = "tfex-example-var"
                          resource_group_name     = azurerm_resource_group.example.name
                          automation_account_name = azurerm_automation_account.example.name
                          value                   = "Hello, Terraform Basic Test."
                          encrypted               = true
                        }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_automation_variable_int']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
