import unittest

import hcl2

from checkov.terraform.checks.resource.azure.SecretExpirationDate import check
from checkov.common.models.enums import CheckResult


class TestSecretExpirationDate(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault_secret" "example" {
              name         = "secret-sauce"
              value        = "szechuan"
              key_vault_id = azurerm_key_vault.example.id
            
              tags = {
                environment = "Production"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault_secret']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault_secret" "example" {
              name         = "secret-sauce"
              value        = "szechuan"
              key_vault_id = azurerm_key_vault.example.id
            
              tags = {
                environment = "Production"
              }
              expiration_date = "2020-12-30T20:00:00Z"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault_secret']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
