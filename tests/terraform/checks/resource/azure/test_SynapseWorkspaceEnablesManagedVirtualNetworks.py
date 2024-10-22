import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SynapseWorkspaceEnablesManagedVirtualNetworks import check
from checkov.common.models.enums import CheckResult


class TestSynapseWorkspaceEnablesManagedVirtualNetworks(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_synapse_workspace" "example" {
              name                                 = "example"
              resource_group_name                  = azurerm_resource_group.example.name
              location                             = azurerm_resource_group.example.location
              storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.example.id
              sql_administrator_login              = "sqladminuser"
              sql_administrator_login_password     = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret
              managed_virtual_network_enabled      = false
              aad_admin {
                login     = "AzureAD Admin"
                object_id = "00000000-0000-0000-0000-000000000000"
                tenant_id = "00000000-0000-0000-0000-000000000000"
              }
            
              tags = {
                Env = "production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_synapse_workspace']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_synapse_workspace" "example" {
              name                                 = "example"
              resource_group_name                  = azurerm_resource_group.example.name
              location                             = azurerm_resource_group.example.location
              storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.example.id
              sql_administrator_login              = "sqladminuser"
              sql_administrator_login_password     = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret
              aad_admin {
                login     = "AzureAD Admin"
                object_id = "00000000-0000-0000-0000-000000000000"
                tenant_id = "00000000-0000-0000-0000-000000000000"
              }

              tags = {
                Env = "production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_synapse_workspace']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_synapse_workspace" "example" {
              name                                 = "example"
              resource_group_name                  = azurerm_resource_group.example.name
              location                             = azurerm_resource_group.example.location
              storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.example.id
              sql_administrator_login              = "sqladminuser"
              sql_administrator_login_password     = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret
              managed_virtual_network_enabled      = true                
              aad_admin {
                login     = "AzureAD Admin"
                object_id = "00000000-0000-0000-0000-000000000000"
                tenant_id = "00000000-0000-0000-0000-000000000000"
              }

              tags = {
                Env = "production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_synapse_workspace']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
