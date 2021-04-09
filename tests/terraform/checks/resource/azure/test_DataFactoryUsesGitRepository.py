import unittest

import hcl2

from checkov.terraform.checks.resource.azure.DataFactoryUsesGitRepository import check
from checkov.common.models.enums import CheckResult


class TestDataFactoryUsesGitRepository(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_data_factory" "example" {
              name                = "example"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_data_factory']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_data_factory" "example" {
              name                = "example"
              location            = azurerm_resource_group.example.location
              resource_group_name = azurerm_resource_group.example.name
              github_configuration {
                repository_name = "checkov"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_data_factory']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
