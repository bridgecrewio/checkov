import unittest
from pathlib import Path
from checkov.arm.checks.resource.AzureBatchAccountEndpointAccessDefaultAction import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.check_assertion_utils import checks_report_assertions


class TestAzureBatchAccountEndpointAccessDefaultAction(unittest.TestCase):
    def test_summary(self):
        passing_resources = {
            "Microsoft.Batch/batchAccounts.pass_empty",
            "Microsoft.Batch/batchAccounts.pass_publicNetworkAccess_disabled",
            "Microsoft.Batch/batchAccounts.pass_publicNetworkAccess_enabled_no_network_profile",
            "Microsoft.Batch/batchAccounts.pass_publicNetworkAccess_enabled_no_account_access",
            "Microsoft.Batch/batchAccounts.pass_publicNetworkAccess_enabled_default_action_deny",
        }
        failing_resources = {
            "Microsoft.Batch/batchAccounts.fail_explicit_publicNetworkAccess":
                ["properties/networkProfile/accountAccess/defaultAction"],
            "Microsoft.Batch/batchAccounts.fail_default_publicNetworkAccess":
                ["properties/networkProfile/accountAccess/defaultAction"],
        }

        # given
        test_files_dir = Path(__file__).parent / "example_AzureBatchAccountEndpointAccessDefaultAction.py"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        checks_report_assertions(self, report, passing_resources, failing_resources)


if __name__ == "__main__":
    unittest.main()
