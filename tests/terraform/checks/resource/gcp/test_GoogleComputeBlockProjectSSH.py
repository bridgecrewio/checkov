import unittest
import os
import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeBlockProjectSSH import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.common.models.enums import CheckResult


class TestGoogleComputeBlockProjectSSH(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/test_GoogleComputeBlockProjectSSH"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_compute_instance.success1',
            'google_compute_instance.success2',
            'google_compute_instance.success3',
            'google_compute_instance.success4',
            'google_compute_instance_template.success1',
            'google_compute_instance_template.success2',
            'google_compute_instance_template.success3',
            'google_compute_instance_template.success4',
            'google_compute_instance_from_template.success1',
            'google_compute_instance_from_template.success2',
            'google_compute_instance_from_template.success3',
            'google_compute_instance_from_template.success4',
        }
        failing_resources = {
            'google_compute_instance.fail1',
            'google_compute_instance.fail2',
            'google_compute_instance_template.fail1',
            'google_compute_instance_template.fail2',
            'google_compute_instance_from_template.fail1',
        }
        unknown_resources = {
            'google_compute_instance_from_template.unknown1',
            'google_compute_instance_from_template.unknown2',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])
        #unknown_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 12)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_unknown_1(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_from_template" "default" {
              name         = "test"
              source_instance_template = google_compute_instance_template.default.id
              metadata = {
                foo = "bar"
                hey = "oh"
                }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_from_template']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_unknown_2(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_from_template" "default" {
              name         = "test"
              source_instance_template = google_compute_instance_template.default.id
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_from_template']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

if __name__ == '__main__':
    unittest.main()