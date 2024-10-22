import unittest
import os

from checkov.terraform.checks.resource.gcp.GoogleComputeDefaultServiceAccountFullAccess import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.plan_runner import Runner as PlanRunner


class TestGoogleComputeBootDiskEncryption(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_GoogleComputeDefaultServiceAccountFullAccess"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_compute_instance.pass1',
            'google_compute_instance.pass2',
            'google_compute_instance.broken',
        }
        failing_resources = {
            'google_compute_instance.fail1',
            'google_compute_instance.fail2',
            'google_compute_instance_template.fail3',
            'google_compute_instance_from_template.fail4',
            'google_compute_instance.fail5',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_terraform_plan(self):
        runner = PlanRunner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_path = current_dir + "/example_GoogleComputeDefaultServiceAccountFullAccess/bad.json"
        report = runner.run(files=[test_files_path], runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        failing_resources = {
            "google_compute_instance.bad3",
        }

        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == '__main__':
    unittest.main()