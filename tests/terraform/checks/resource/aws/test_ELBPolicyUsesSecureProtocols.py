import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ELBPolicyUsesSecureProtocols import check
from checkov.terraform.runner import Runner


class TestELBPolicyUsesSecureProtocols(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ELBPolicyUsesSecureProtocols"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_load_balancer_policy.pass",
            "aws_load_balancer_policy.pass2",
            "aws_load_balancer_policy.pass3",
        }
        failing_resources = {
            "aws_load_balancer_policy.fail",
            "aws_load_balancer_policy.fail2",
            "aws_load_balancer_policy.fail3",
            "aws_load_balancer_policy.fail4",
            "aws_load_balancer_policy.fail5",
            "aws_load_balancer_policy.fail6",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 6)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
