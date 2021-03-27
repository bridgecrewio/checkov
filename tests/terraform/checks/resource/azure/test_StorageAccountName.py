import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.StorageAccountName import check


class TestAzureStorageAccountNamingRule(unittest.TestCase):
    def test_failure_dash(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_storage_account" "example" {
              name                     = "this-is-wrong"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_storage_account"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_length(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_storage_account" "example" {
              name                     = "thisiswayyyyyytoooloooong"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_storage_account"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_case(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_storage_account" "example" {
              name                     = "thisIsWrong"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_storage_account"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_storage_account" "example" {
              name                     = "stomyexample"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_storage_account"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_empty_configuration(self):
        hcl_res = hcl2.loads(
            """
            resource "azurerm_storage_account" "example" {
            }
                """
        )
        resource_conf = hcl_res["resource"][0]["azurerm_storage_account"]["example"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
