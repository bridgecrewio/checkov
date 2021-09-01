import unittest

import hcl2

from checkov.terraform.checks.resource.azure.CosmosDBDisableAccessKeyWrite import check
from checkov.common.models.enums import CheckResult


class TestCosmosDBDisableAccessKeyWrite(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_cosmosdb_account" "db" {
              name                = "tfex-cosmos-db-${random_integer.ri.result}"
              location            = azurerm_resource_group.rg.location
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
              access_key_metadata_writes_enabled = false
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_cosmosdb_account']['db']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
