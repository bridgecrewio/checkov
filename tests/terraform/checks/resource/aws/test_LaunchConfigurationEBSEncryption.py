import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.LaunchConfigurationEBSEncryption import check
from checkov.terraform.runner import Runner


class TestLaunchConfigurationEBSEncryption(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_LaunchConfigurationEBSEncryption"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_instance.pass",
            "aws_instance.pass2",
            "aws_instance.pass3",
            "aws_launch_configuration.pass",
            "aws_launch_configuration.pass2",
        }
        failing_resources = {
            "aws_instance.fail",
            "aws_instance.fail2",
            "aws_instance.fail3",
            "aws_instance.fail4",
            "aws_instance.fail5",
            "aws_instance.fail_empty_root_list",
            "aws_launch_configuration.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 5)
        self.assertEqual(summary["failed"], 7)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
