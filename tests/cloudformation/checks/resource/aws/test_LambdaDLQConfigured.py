import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.LambdaDLQConfigured import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestLambdaDLQConfigured(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_LambdaDLQConfigured"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::Lambda::Function.Enabled",
            "AWS::Serverless::Function.Enabled",
        }
        failing_resources = {
            "AWS::Lambda::Function.Default",
            "AWS::Serverless::Function.Default",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
