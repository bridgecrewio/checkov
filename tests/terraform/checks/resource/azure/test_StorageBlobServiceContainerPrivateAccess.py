import unittest

import hcl2

from checkov.terraform.checks.resource.azure.StorageBlobServiceContainerPrivateAccess import check
from checkov.common.models.enums import CheckResult


class TestStorageBlobServiceContainerPrivateAccess(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_container" "example" {
              name                  = "vhds"
              storage_account_name  = azurerm_storage_account.example.name
              container_access_type = "blob"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_container']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_container" "example" {
              name                  = "vhds"
              storage_account_name  = azurerm_storage_account.example.name
              container_access_type = "private"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_container']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
