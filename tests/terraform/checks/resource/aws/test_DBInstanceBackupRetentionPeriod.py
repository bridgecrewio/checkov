import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.DBInstanceBackupRetentionPeriod import check
from checkov.terraform.runner import Runner


class TestDBInstanceBackupRetentionPeriod(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_DBInstanceBackupRetentionPeriod"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_rds_cluster.pass",
            "aws_db_instance.pass",
            "aws_rds_cluster.pass2",
            "aws_db_instance.pass2",
        }
        failing_resources = {
            "aws_rds_cluster.fail",
            "aws_rds_cluster.fail2",
            "aws_db_instance.fail",
            "aws_db_instance.fail2",
        }
        unknown_resources = {
            "aws_db_instance.unknown"
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)
        self.assertEqual(len([r for r in report.resources if r in unknown_resources]), 0)


if __name__ == "__main__":
    unittest.main()
