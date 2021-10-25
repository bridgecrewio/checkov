import os
import unittest

from checkov.cloudformation.checks.resource.aws.CloudFrontTLS12 import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCloudFrontTLS12(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_CloudFrontTLS12"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'AWS::CloudFront::Distribution.cloudfrontdistributionPASSED1',
            'AWS::CloudFront::Distribution.cloudfrontdistributionPASSED2',
            'AWS::CloudFront::Distribution.cloudfrontdistributionPASSED3'
        }

        failing_resources = {
            'AWS::CloudFront::Distribution.cloudfrontdistributionFAILED1',
            'AWS::CloudFront::Distribution.cloudfrontdistributionFAILED2',
            'AWS::CloudFront::Distribution.cloudfrontdistributionFAILED3',
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