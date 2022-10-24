import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.RedshiftClusterPubliclyAccessible import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRedshiftClusterPubliclyAccessible(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_RedshiftClusterPubliclyAccessible"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::Redshift::Cluster.RedshiftClusterEnabled",
        }
        failing_resources = {
            "AWS::Redshift::Cluster.RedshiftClusterDefault",
            "AWS::Redshift::Cluster.RedshiftClusterDisabled",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
