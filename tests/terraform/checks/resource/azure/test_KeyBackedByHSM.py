import unittest
from pathlib import Path

import hcl2

from checkov.terraform.checks.resource.azure.KeyBackedByHSM import check
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


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


    def test_optional_type_defaults_with_foreach(self):
        """Regression test for https://github.com/bridgecrewio/checkov/issues/4874

        When a variable uses optional(string, "RSA-HSM") in its type constraint and
        the default value doesn't explicitly set that field, checkov must resolve the
        optional default. Without the fix, key_type remains unresolved and the check
        incorrectly fails.
        """
        test_dir = Path(__file__).parent / "example_KeyBackedByHSM_optional"
        report = Runner().run(
            root_folder=str(test_dir),
            runner_filter=RunnerFilter(checks=[check.id]),
        )

        passed_resources = {c.resource for c in report.passed_checks}
        failed_resources = {c.resource for c in report.failed_checks}

        # for_each with optional(string, "RSA-HSM") -- should PASS
        self.assertTrue(
            any("foreach_pass" in r for r in passed_resources),
            f"Expected foreach_pass resource to PASS CKV_AZURE_112. "
            f"Passed: {passed_resources}, Failed: {failed_resources}"
        )

        # for_each with optional(string, "RSA") (non-HSM) -- should FAIL
        self.assertTrue(
            any("foreach_fail" in r for r in failed_resources),
            f"Expected foreach_fail resource to FAIL CKV_AZURE_112. "
            f"Passed: {passed_resources}, Failed: {failed_resources}"
        )

        # 3-level nested: optional(string, "RSA-HSM") at deepest level -- should PASS
        self.assertTrue(
            any("nested_pass" in r for r in passed_resources),
            f"Expected nested_pass to PASS CKV_AZURE_112 (3-level nested). "
            f"Passed: {passed_resources}, Failed: {failed_resources}"
        )

        # 3-level nested: optional(string, "RSA") at deepest level -- should FAIL
        self.assertTrue(
            any("nested_fail" in r for r in failed_resources),
            f"Expected nested_fail to FAIL CKV_AZURE_112 (3-level nested). "
            f"Passed: {passed_resources}, Failed: {failed_resources}"
        )


if __name__ == '__main__':
    unittest.main()
