import unittest
import os
from pathlib import Path
from unittest import mock

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.NetworkACLUnrestrictedIngress3389 import check
from checkov.terraform.runner import Runner


class TestNetworkACLUnrestrictedIngress3389(unittest.TestCase):
    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_NetworkACLUnrestrictedIngress3389"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_network_acl.pass",
            "aws_network_acl.pass2",
            "aws_network_acl.pass3",
            "aws_network_acl_rule.pass",
            "aws_network_acl_rule.pass2",
            "aws_network_acl_rule.count_pass",
        }
        failing_resources = {
            "aws_network_acl.fail",
            "aws_network_acl.fail2",
            "aws_network_acl.fail3",
            "aws_network_acl.fail4",
            "aws_network_acl_rule.fail",
            "aws_network_acl_rule.fail2",
            "aws_network_acl_rule.public_ingress",
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
