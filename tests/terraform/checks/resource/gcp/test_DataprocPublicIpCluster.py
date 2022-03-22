import unittest
import os

from checkov.terraform.checks.resource.gcp.DataprocPublicIpCluster import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestDataprocPublicIpCluster(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_DataprocPublicIpCluster"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_dataproc_cluster.pass1',
        }
        failing_resources = {
            'google_dataproc_cluster.fail1',
            'google_dataproc_cluster.fail2',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
