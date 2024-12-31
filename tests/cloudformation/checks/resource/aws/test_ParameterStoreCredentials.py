import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.ParameterStoreCredentials import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestParameterStoreCredentials(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_ParameterStoreCredentials"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::SSM::Parameter.GoodNoKeyword",
            "AWS::SSM::Parameter.GoodVariable",
            "AWS::SSM::Parameter.GoodFnSub",
            "AWS::SSM::Parameter.GoodRef",
            "AWS::SSM::Parameter.PassTestName",
            "AWS::SSM::Parameter.PassTestVALUE",
        }
        failing_resources = {
            "AWS::SSM::Parameter.FailAPIKey",
            "AWS::SSM::Parameter.Bad1",
            "AWS::SSM::Parameter.Bad2",
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
