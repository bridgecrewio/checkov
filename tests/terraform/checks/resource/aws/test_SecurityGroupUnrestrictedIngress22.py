import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress22 import check
from checkov.terraform.runner import Runner


class TestSecurityGroupUnrestrictedIngress22(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_SecurityGroupUnrestrictedIngress22"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_security_group.pass",
            "aws_security_group.pass2",
            "aws_security_group.pass3",
            "aws_security_group.pass4",
            "aws_security_group.pass5",
            "aws_security_group.pass6",
            "aws_security_group.pass7",
            "aws_security_group.pass-ipv6",
            "aws_security_group_rule.pass",
            "aws_security_group_rule.pass2",
            "aws_security_group_rule.pass3",
            "aws_security_group_rule.pass4",
            "aws_vpc_security_group_ingress_rule.pass",
            "aws_security_group.pass_self",
            "aws_security_group.pass_self2"
        }

        failing_resources = {
            "aws_security_group.fail",
            "aws_security_group.fail2",
            "aws_security_group.fail3",
            "aws_security_group.fail4",
            "aws_security_group.fail-ipv6",
            "aws_security_group_rule.fail",
            "aws_vpc_security_group_ingress_rule.fail",
            "aws_vpc_security_group_ingress_rule.fail2",
            "aws_security_group.not_self"
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
