import unittest
import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.azure.AzureManagedDiscEncryption import check


class TestAzureManagedDiscEncryption(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_managed_disk" "example" {
                name                 = var.disk_name
                location             = var.location
                resource_group_name  = var.resource_group_name
                storage_account_type = var.storage_account_type
                create_option        = "Empty"
                disk_size_gb         = var.disk_size_gb
                encryption_settings {
                    enabled = false
                    }
                tags = var.common_tags
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_managed_disk']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def testmissing_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_managed_disk" "example" {
                name                 = var.disk_name
                location             = var.location
                resource_group_name  = var.resource_group_name
                storage_account_type = var.storage_account_type
                create_option        = "Empty"
                disk_size_gb         = var.disk_size_gb
                tags = var.common_tags
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_managed_disk']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_managed_disk" "example" {
                name                 = var.disk_name
                location             = var.location
                resource_group_name  = var.resource_group_name
                storage_account_type = var.storage_account_type
                create_option        = "Empty"
                disk_size_gb         = var.disk_size_gb
                encryption_settings {
                    enabled = true
                    }
                tags = var.common_tags
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_managed_disk']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
