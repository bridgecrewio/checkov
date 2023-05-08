import unittest
import os
from pathlib import Path
from unittest import mock

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.NetworkFirewallPolicyDefinesCMK import check
from checkov.terraform.runner import Runner


class TestNetworkFirewallPolicyDefinesCMK(unittest.TestCase):
    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_NetworkFirewallPolicyDefinesCMK"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_networkfirewall_firewall_policy.pass",
        }
        failing_resources = {
            "aws_networkfirewall_firewall_policy.fail",
            "aws_networkfirewall_firewall_policy.fail2",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
