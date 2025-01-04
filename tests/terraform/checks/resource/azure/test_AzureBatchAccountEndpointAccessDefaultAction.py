import os
import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.azure.AzureBatchAccountEndpointAccessDefaultAction import check
from tests.common.check_assertion_utils import checks_report_assertions


class TestAzureBatchAccountEndpointAccessDefaultAction(unittest.TestCase):

    def test(self):
        runner = Runner()

        test_files_dir = Path(__file__).parent / "example_AzureBatchAccountEndpointAccessDefaultAction"
        report = runner.run(root_folder=str(test_files_dir),
                            runner_filter=RunnerFilter(checks=[check.id]))

        passing_resources = {
            'azurerm_batch_account.pass_no_publicNetworkAccess',
            'azurerm_batch_account.pass_publicNetworkAccess_disabled',
            'azurerm_batch_account.pass_publicNetworkAccess_enabled_no_network_profile',
            'azurerm_batch_account.pass_publicNetworkAccess_enabled_no_account_access',
            'azurerm_batch_account.pass_publicNetworkAccess_enabled_default_action_deny',

        }
        failing_resources = {
            'azurerm_batch_account.fail_publicNetworkAccess_enabled_default_action_allow',
            'azurerm_batch_account.fail_bad_default_action_no_public_network',
        }

        # then
        checks_report_assertions(self, report, passing_resources, failing_resources)


if __name__ == '__main__':
    unittest.main()