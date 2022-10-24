import unittest
import os

from checkov.terraform.checks.resource.gcp.BigQueryPrivateTable import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestBigQueryPrivateTable(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_BigQueryPrivateTable"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_bigquery_table_iam_binding.pass1',
            'google_bigquery_table_iam_binding.pass2',
            'google_bigquery_table_iam_member.pass1',
            'google_bigquery_table_iam_member.pass2',

        }
        failing_resources = {
            'google_bigquery_table_iam_binding.fail1',
            'google_bigquery_table_iam_binding.fail2',
            'google_bigquery_table_iam_binding.fail3',
            'google_bigquery_table_iam_binding.fail4',
            'google_bigquery_table_iam_member.fail1',
            'google_bigquery_table_iam_member.fail2',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 6)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
