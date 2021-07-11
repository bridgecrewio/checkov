import os
import unittest

from checkov.cloudformation.checks.resource.aws.CloudWatchLogGroupRetention import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCloudWatchLogGroupRetention(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_CloudWatchLogGroupRetention"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        for record in report.failed_checks:
            self.assertEqual(record.check_id, check.id)
        
        for record in report.passed_checks:
            self.assertEqual(record.check_id, check.id)

        passing_resources = {
            "AWS::Logs::LogGroup.Pass",
        }

        failing_resources = {
            "AWS::Logs::LogGroup.Fail",

        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
