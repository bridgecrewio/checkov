import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.StorageAccountMinimumTlsVersion import check


class TestAppServiceMinTLSVersion(unittest.TestCase):

    def test_failure_option_not_present(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_insecure_option_present_tls10(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              min_tls_version          = "TLS1_0"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_insecure_option_present_tls11(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              min_tls_version          = "TLS1_1"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_secure_option_present(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              min_tls_version          = "TLS1_2"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_future_option_present(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_account" "example" {
              name                     = "example"
              resource_group_name      = data.azurerm_resource_group.example.name
              location                 = data.azurerm_resource_group.example.location
              account_tier             = "Standard"
              account_replication_type = "GRS"
              min_tls_version          = "TLS1_3"
              network_rules {
                default_action             = "Allow"
                ip_rules                   = ["100.0.0.1"]
                virtual_network_subnet_ids = [azurerm_subnet.example.id]
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_account']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
