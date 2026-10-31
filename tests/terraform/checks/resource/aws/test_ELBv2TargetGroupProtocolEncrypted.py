import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ELBv2TargetGroupProtocolEncrypted import check
from checkov.terraform.runner import Runner


class TestELBv2TargetGroupProtocolEncrypted(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_ELBv2TargetGroupProtocolEncrypted")
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_lb_target_group.pass_https",
            "aws_lb_target_group.pass_tls",
            "aws_lb_target_group.pass_lambda",
            "aws_alb_target_group.pass_alb_https",
        }
        failing_resources = {
            "aws_lb_target_group.fail_http",
            "aws_lb_target_group.fail_tcp",
            "aws_lb_target_group.fail_udp",
            "aws_lb_target_group.fail_no_protocol",
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
