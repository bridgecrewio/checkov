import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.data.aws.AWSAvailabilityZonesUnfiltered import check


class TestAWSAvailabilityZonesUnfiltered(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_AWSAvailabilityZonesUnfiltered")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'aws_availability_zones.filtered_by_name',
            'aws_availability_zones.filtered_by_id',
        }
        failing_resources = {
            'aws_availability_zones.unfiltered',
            'aws_availability_zones.state_only',
            'aws_availability_zones.filter_opt_in_status',
            'aws_availability_zones.excluded_by_name',
            'aws_availability_zones.excluded_by_id',
        }
        skipped_resources = {}

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()