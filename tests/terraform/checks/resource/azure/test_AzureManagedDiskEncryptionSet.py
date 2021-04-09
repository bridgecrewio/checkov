import unittest

import hcl2

from checkov.terraform.checks.resource.azure.AzureManagedDiskEncryptionSet import check
from checkov.common.models.enums import CheckResult


class TestAzureManagedDiskEncryptionSet(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_managed_disk" "source" {
              name                 = "acctestmd1"
              location             = "West US 2"
              resource_group_name  = azurerm_resource_group.example.name
              storage_account_type = "Standard_LRS"
              create_option        = "Empty"
              disk_size_gb         = "1"
            
              tags = {
                environment = "staging"
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_managed_disk']['source']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "azurerm_managed_disk" "source" {
              name                 = "acctestmd1"
              location             = "West US 2"
              resource_group_name  = azurerm_resource_group.example.name
              storage_account_type = "Standard_LRS"
              create_option        = "Empty"
              disk_size_gb         = "1"
              disk_encryption_set_id = "koko"
              tags = {
                environment = "staging"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_managed_disk']['source']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
