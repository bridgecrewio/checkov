import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.ncp.NACLInbound21 import check
from checkov.terraform.runner import Runner


class TestNACLInbound21(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_NACLInbound21"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "ncloud_network_acl_rule.pass",
            "ncloud_network_acl_rule.pass1"
        }
        failing_resources = {
            "ncloud_network_acl_rule.fail",
            "ncloud_network_acl_rule.fail1",
            "ncloud_network_acl_rule.fail2"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 3)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()