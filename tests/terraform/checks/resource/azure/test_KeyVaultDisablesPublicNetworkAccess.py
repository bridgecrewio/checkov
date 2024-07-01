import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.azure.KeyVaultDisablesPublicNetworkAccess import check


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
            'azurerm_key_vault.pass5'
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


if __name__ == '__main__':
    unittest.main()