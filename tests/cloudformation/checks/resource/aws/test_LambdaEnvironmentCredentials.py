import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.LambdaEnvironmentCredentials import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestLambdaEnvironmentCredentials(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_LambdaEnvironmentCredentials"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::Lambda::Function.NoEnv",
            "AWS::Lambda::Function.NoSecret",
            "AWS::Lambda::Function.EnvNull",
            "AWS::Lambda::Function.UnresolvedEnv",
            "AWS::Serverless::Function.NoEnv",
            "AWS::Serverless::Function.NoProperties",
            "AWS::Serverless::Function.NoSecret",
            "AWS::Lambda::Function.Pass2",
            "AWS::Lambda::Function.CDKLambda",
        }
        failing_resources = {
            "AWS::Lambda::Function.Secret",
            "AWS::Serverless::Function.Secret",
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
