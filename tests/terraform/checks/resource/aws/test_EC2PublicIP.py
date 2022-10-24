import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.EC2PublicIP import check
from checkov.terraform.runner import Runner


class TestEC2PublicIP(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_EC2PublicIP"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_instance.default",
            "aws_instance.private",
            "aws_launch_template.default",
            "aws_launch_template.private",
        }
        failing_resources = {
            "aws_instance.public",
            "aws_launch_template.public",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
