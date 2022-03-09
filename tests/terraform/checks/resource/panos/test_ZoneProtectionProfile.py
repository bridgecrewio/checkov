import unittest
import os

from checkov.terraform.checks.resource.panos.ZoneProtectionProfile import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestZoneProtectionProfile(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ZoneProtectionProfile"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'panos_zone.pass1',
            'panos_zone_entry.pass2',
            'panos_panorama_zone.pass3',
        }
        failing_resources = {
            'panos_zone.fail1',
            'panos_zone_entry.fail2',
            'panos_panorama_zone.fail3',
            'panos_zone.fail4',
            'panos_zone_entry.fail5',
            'panos_panorama_zone.fail6',
            'panos_zone.fail7',
            'panos_zone_entry.fail8',
            'panos_panorama_zone.fail9',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 9)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
