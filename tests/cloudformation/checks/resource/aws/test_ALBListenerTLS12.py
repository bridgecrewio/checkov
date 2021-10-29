import os
import unittest

from checkov.cloudformation.checks.resource.aws.ALBListenerTLS12 import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestALBListenerTLS12(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ALBListenerTLS12"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSPASSED1',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSPASSED2',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPPASSED3'
        }

        failing_resources = {
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSFAILED1',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSFAILED2'
        }
        
        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == '__main__':
    unittest.main()
