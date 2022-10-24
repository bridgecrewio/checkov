import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.IMDSv1Disabled import check
from checkov.terraform.runner import Runner


class TestIMDSv1Disabled(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_IMDSv1Disabled"
        report = runner.run(
            root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id])
        )
        summary = report.get_summary()

        passing_resources = {
            "aws_instance.required",
            "aws_launch_configuration.required_lc",
            "aws_instance.disabled"
        }
        failing_resources = {
            "aws_instance.defaults",
            "aws_instance.optional_token",
            "aws_launch_configuration.optional_lc",
            "aws_launch_template.optional_lt",
            "aws_launch_template.default_lt"
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 5)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
