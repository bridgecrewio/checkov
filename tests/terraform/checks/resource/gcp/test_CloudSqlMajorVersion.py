import unittest
import os

from checkov.terraform.checks.resource.gcp.CloudSqlMajorVersion import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestCloudSqlMajorVersion(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_CloudSqlMajorVersion"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_sql_database_instance.pass',
            'google_sql_database_instance.pass2',
            'google_sql_database_instance.pass3',
        }
        failing_resources = {
            'google_sql_database_instance.fail',
            'google_sql_database_instance.fail2',
            'google_sql_database_instance.fail3',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()