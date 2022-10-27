import unittest

import hcl2

from checkov.terraform.checks.resource.azure.StorageSyncPublicAccessDisabled import check
from checkov.common.models.enums import CheckResult


class TestStorageSyncPublicAccessDisabled(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_sync" "test" {
              name                = "example-storage-sync"
              resource_group_name = azurerm_resource_group.test.name
              location            = azurerm_resource_group.test.location
              tags = {
                foo = "bar"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_sync']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_sync" "test" {
              name                = "example-storage-sync"
              resource_group_name = azurerm_resource_group.test.name
              location            = azurerm_resource_group.test.location
              incoming_traffic_policy = "AllowAllTraffic"
              tags = {
                foo = "bar"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_sync']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_storage_sync" "test" {
              name                = "example-storage-sync"
              resource_group_name = azurerm_resource_group.test.name
              location            = azurerm_resource_group.test.location
              incoming_traffic_policy = "AllowVirtualNetworksOnly"
              tags = {
                foo = "bar"
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['azurerm_storage_sync']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
