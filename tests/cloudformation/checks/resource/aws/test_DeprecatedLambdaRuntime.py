import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.DeprecatedLambdaRuntime import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestDeprecatedLambdaRuntime(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_DeprecatedLambdaRuntime"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "AWS::Lambda::Function.Pass",
            "AWS::Serverless::Function.Pass2"
        }
        failing_resources = {
            "AWS::Lambda::Function.Fail",
            "AWS::Serverless::Function.Fail2",
            "AWS::Lambda::Function.Fail-java8"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
