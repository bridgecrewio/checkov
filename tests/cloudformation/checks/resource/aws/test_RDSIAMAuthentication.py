import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.RDSIAMAuthentication import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRDSIAMAuthentication(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_RDSIAMAuthentication"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::RDS::DBInstance.EnabledMysql",
            "AWS::RDS::DBInstance.EnabledPostgres",
        }
        failing_resources = {
            "AWS::RDS::DBInstance.DefaultMysql",
            "AWS::RDS::DBInstance.DefaultPostgres",
            "AWS::RDS::DBInstance.DisabledMysql",
            "AWS::RDS::DBInstance.DisabledPostgres",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
