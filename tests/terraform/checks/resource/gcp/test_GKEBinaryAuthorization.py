import unittest
import os

from checkov.terraform.checks.resource.gcp.GKEBinaryAuthorization import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestGKEBinaryAuthorization(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/test_GKEBinaryAuthorization"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_container_cluster.success',
            'google_container_cluster.success2'
        }
        failing_resources = {
            'google_container_cluster.fail1',
            'google_container_cluster.fail2',
            'google_container_cluster.fail3',
            'google_container_cluster.fail4',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 4)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()