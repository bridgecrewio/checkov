import os
import unittest

import hcl2

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.azure.KeyVaultDisablesPublicNetworkAccess import check
from checkov.common.models.enums import CheckResult


class TestKeyVaultDisablesPublicNetworkAccess(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_KeyVaultDisablesPublicNetworkAccess")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'azurerm_key_vault.pass1',
            'azurerm_key_vault.pass2',
            'azurerm_key_vault.pass3',
            'azurerm_key_vault.pass4',
            'azurerm_key_vault.pass5',
            'azurerm_key_vault.pass6'
        }
        failing_resources = {
            'azurerm_key_vault.fail1',
            'azurerm_key_vault.fail2',
            'azurerm_key_vault.fail3',
            'azurerm_key_vault.fail4',
            'azurerm_key_vault.fail5'

        }

        skipped_resources = {}

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def _build_conf(self, network_acls_block):
        hcl_res = hcl2.loads(f"""
                resource "azurerm_key_vault" "example" {{
                  name                                    = "examplekeyvault"
                  location                                = azurerm_resource_group.example.location
                  resource_group_name                     = azurerm_resource_group.example.name
                  public_network_access_enabled           = true
                  sku_name                                = "standard"
                  {network_acls_block}
                }}
                """)
        return hcl_res['resource'][0]['azurerm_key_vault']['example']

    def test_deny_empty_ip_rules_passes(self):
        resource_conf = self._build_conf("""
                  network_acls {
                    default_action = "Deny"
                    ip_rules       = []
                  }
                """)
        self.assertEqual(CheckResult.PASSED, check.scan_resource_conf(conf=resource_conf))

    def test_allow_empty_ip_rules_fails(self):
        resource_conf = self._build_conf("""
                  network_acls {
                    default_action = "Allow"
                    ip_rules       = []
                  }
                """)
        self.assertEqual(CheckResult.FAILED, check.scan_resource_conf(conf=resource_conf))

    def test_unknown_default_action_with_empty_ip_rules_fails(self):
        resource_conf = self._build_conf("""
                  network_acls {
                    default_action = var.action
                    ip_rules       = []
                  }
                """)
        self.assertEqual(CheckResult.FAILED, check.scan_resource_conf(conf=resource_conf))

    def test_deny_normalized_empty_ip_rules_passes(self):
        # A rendered/normalized pipeline can present ip_rules as a bare [] list
        # (instead of the raw HCL parser's [[]]).
        resource_conf = {
            "public_network_access_enabled": [True],
            "network_acls": [
                {
                    "default_action": ["Deny"],
                    "ip_rules": [],
                }
            ],
        }
        self.assertEqual(CheckResult.PASSED, check.scan_resource_conf(conf=resource_conf))



if __name__ == '__main__':
    unittest.main()