import unittest
import os

from checkov.terraform.checks.resource.gcp.GoogleComputeDefaultServiceAccount import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestGoogleComputeDefaultServiceAccount(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_GoogleComputeDefaultServiceAccount"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_compute_instance.pass1',
            'google_compute_instance.pass2',
            'google_compute_instance_template.pass3',
            'google_compute_instance_from_template.pass4'
        }
        failing_resources = {
            'google_compute_instance.fail2',
            'google_compute_instance_from_template.fail3'
        }
        # unknown_resources = {
        #     'google_compute_instance_from_template.unknown1',
        #     'google_compute_instance.unknown2'
        # }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
