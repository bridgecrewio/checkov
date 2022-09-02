import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.ECRPolicy import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestECRPolicy(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_ECRPolicy"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "AWS::ECR::Repository.Restricted",
            "AWS::ECR::Repository.vpc16AA8B31E",
            "AWS::ECR::Repository.CondAllPass",
            "AWS::ECR::Repository.CondAnyPass",
            "AWS::ECR::Repository.CondEqualsPass",
        }
        failing_resources = {
            "AWS::ECR::Repository.Public",
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
