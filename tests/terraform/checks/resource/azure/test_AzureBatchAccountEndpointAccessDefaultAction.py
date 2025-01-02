import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.azure.AzureBatchAccountEndpointAccessDefaultAction import check


class TestAzureBatchAccountEndpointAccessDefaultAction(unittest.TestCase):

    def test(self):
        runner = Runner()

        test_files_dir = Path(__file__).parent / "example_AzureBatchAccountEndpointAccessDefaultAction"
        report = runner.run(root_folder=str(test_files_dir),
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'azurerm_batch_account.pass_no_publicNetworkAccess',
            'azurerm_batch_account.pass_publicNetworkAccess_disabled',
            'azurerm_batch_account.pass_publicNetworkAccess_enabled_no_network_profile',
            'azurerm_batch_account.pass_publicNetworkAccess_enabled_no_account_access',
            'azurerm_batch_account.pass_publicNetworkAccess_enabled_default_action_deny',

        }
        failing_resources = {
            'azurerm_batch_account.fail_publicNetworkAccess_enabled_default_action_allow',
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