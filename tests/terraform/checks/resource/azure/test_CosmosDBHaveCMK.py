import unittest

import hcl2

from checkov.terraform.checks.resource.azure.CosmosDBHaveCMK import check
from checkov.common.models.enums import CheckResult


class TestCosmosDBHaveCMK(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
           resource "azurerm_cosmosdb_account" "db" {
              name                = "tfex-cosmos-db-${random_integer.ri.result}"
              location            = azurerm_resource_group.rg.location
              resource_group_name = azurerm_resource_group.rg.name
              offer_type          = "Standard"
              kind                = "GlobalDocumentDB"
            
              enable_automatic_failover = true
            
              capabilities {
                name = "EnableAggregationPipeline"
              }
            
              capabilities {
                name = "mongoEnableDocLevelTTL"
              }
            
              capabilities {
                name = "MongoDBv3.4"
              }
            
              consistency_policy {
                consistency_level       = "BoundedStaleness"
                max_interval_in_seconds = 10
                max_staleness_prefix    = 200
              }
            
              geo_location {
                location          = var.failover_location
                failover_priority = 1
              }
            
              geo_location {
                location          = azurerm_resource_group.rg.location
                failover_priority = 0
              }
            }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_cosmosdb_account']['db']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_cosmosdb_account" "db" {
                  name                = "tfex-cosmos-db-${random_integer.ri.result}"
                  location            = azurerm_resource_group.rg.location
                  resource_group_name = azurerm_resource_group.rg.name
                  offer_type          = "Standard"
                  kind                = "GlobalDocumentDB"
                
                  enable_automatic_failover = true
                
                  capabilities {
                    name = "EnableAggregationPipeline"
                  }
                
                  capabilities {
                    name = "mongoEnableDocLevelTTL"
                  }
                
                  capabilities {
                    name = "MongoDBv3.4"
                  }
                
                  consistency_policy {
                    consistency_level       = "BoundedStaleness"
                    max_interval_in_seconds = 10
                    max_staleness_prefix    = 200
                  }
                
                  geo_location {
                    location          = var.failover_location
                    failover_priority = 1
                  }
                
                  geo_location {
                    location          = azurerm_resource_group.rg.location
                    failover_priority = 0
                  }
                  
                  key_vault_key_id = "A versionless Key Vault Key ID for CMK encryption"
                }
            """)
        resource_conf = hcl_res['resource'][0]['azurerm_cosmosdb_account']['db']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
