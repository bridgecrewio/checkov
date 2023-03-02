import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription import check
from checkov.terraform.runner import Runner


class TestSecurityGroupRuleDescription(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_SecurityGroupRuleDescription"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_security_group.pass",
            "aws_security_group.pass2",
            "aws_security_group_rule.pass",
            "aws_vpc_security_group_ingress_rule.pass"
        }

        failing_resources = {
            "aws_security_group.fail",
            "aws_security_group_rule.fail",
            "aws_vpc_security_group_ingress_rule.fail"
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
