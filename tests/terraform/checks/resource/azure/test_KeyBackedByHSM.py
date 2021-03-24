import unittest

import hcl2

from checkov.terraform.checks.resource.azure.KeyBackedByHSM import check
from checkov.common.models.enums import CheckResult


class TestKeyBackedByHSM(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault_key" "generated" {
              name         = "generated-certificate"
              key_vault_id = azurerm_key_vault.example.id
              key_type     = "RSA"
              key_size     = 2048
            
              key_opts = [
                "decrypt",
                "encrypt",
                "sign",
                "unwrapKey",
                "verify",
                "wrapKey",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault_key']['generated']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success1(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault_key" "generated" {
              name         = "generated-certificate"
              key_vault_id = azurerm_key_vault.example.id
              key_type     = "EC-HSM"
              key_size     = 2048
            
              key_opts = [
                "decrypt",
                "encrypt",
                "sign",
                "unwrapKey",
                "verify",
                "wrapKey",
              ]
              expiration_date = "2020-12-30T20:00:00Z"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault_key']['generated']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
            resource "azurerm_key_vault_key" "generated" {
              name         = "generated-certificate"
              key_vault_id = azurerm_key_vault.example.id
              key_type     = "RSA-HSM"
              key_size     = 2048

              key_opts = [
                "decrypt",
                "encrypt",
                "sign",
                "unwrapKey",
                "verify",
                "wrapKey",
              ]
              expiration_date = "2020-12-30T20:00:00Z"
            }
                """)
        resource_conf = hcl_res['resource'][0]['azurerm_key_vault_key']['generated']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
