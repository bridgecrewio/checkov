import logging
import unittest
from pathlib import Path

from checkov.arm.checks.resource.AzureSynapseWorkspacesHaveNoIPFirewallRulesAttached import check

from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestSynapseWorkspaceHaveNoIPFirewallRulesAttached(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_AzureSynapseWorkspacesHaveNoIPFirewallRulesAttached"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()
        logging.warning(f"summary:  {summary}")

        passing_resources = {
            "azurerm_synapse_workspace.pass",
            "azurerm_synapse_workspace.pass2",
        }
        failing_resources = {
            "azurerm_synapse_workspace.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 3)  # 3 unknown

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
