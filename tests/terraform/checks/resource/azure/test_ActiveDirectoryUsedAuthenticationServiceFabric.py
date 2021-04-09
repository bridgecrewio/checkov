import unittest

import hcl2

from checkov.terraform.checks.resource.azure.ActiveDirectoryUsedAuthenticationServiceFabric import check
from checkov.common.models.enums import CheckResult


class TestActiveDirectoryUsedAuthenticationServiceFabric(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_service_fabric_cluster" "example" {
              name                 = "example-servicefabric"
              resource_group_name  = azurerm_resource_group.example.name
              location             = azurerm_resource_group.example.location
              reliability_level    = "Bronze"
              upgrade_mode         = "Manual"
              cluster_code_version = "7.1.456.959"
              vm_image             = "Windows"
              management_endpoint  = "https://example:80"
            
              node_type {
                name                 = "first"
                instance_count       = 3
                is_primary           = true
                client_endpoint_port = 2020
                http_endpoint_port   = 80
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_service_fabric_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_service_fabric_cluster" "example" {
              name                 = "example-servicefabric"
              resource_group_name  = azurerm_resource_group.example.name
              location             = azurerm_resource_group.example.location
              reliability_level    = "Bronze"
              upgrade_mode         = "Manual"
              cluster_code_version = "7.1.456.959"
              vm_image             = "Windows"
              management_endpoint  = "https://example:80"
              azure_active_directory {
                tenant_id = "tenant"
              }
              node_type {
                name                 = "first"
                instance_count       = 3
                is_primary           = true
                client_endpoint_port = 2020
                http_endpoint_port   = 80
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_service_fabric_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
