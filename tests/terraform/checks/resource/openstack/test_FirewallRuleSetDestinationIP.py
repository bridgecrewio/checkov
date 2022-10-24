import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.openstack.FirewallRuleSetDestinationIP import check
from checkov.terraform.runner import Runner


class TestFirewallRuleSetDestinationIP(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_FirewallRuleSetDestinationIP"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "openstack_fw_rule_v1.pass",
        }
        failing_resources = {
            "openstack_fw_rule_v1.fail",
            "openstack_fw_rule_v1.fail-cidr",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()