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
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPPASSED2',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTLSPASSED1',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTLSPASSED2',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTLSPASSED3',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTCPPASSED4',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSPASS13'
        }

        failing_resources = {
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSFAILED1',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPSFAILED2',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTLSFAILED1',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTLSFAILED2',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerTLSFAILED3',
            'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPFAILED1'
        }

        unknown_resource = 'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPUnknown'
        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], passing_resources.__len__())
        self.assertEqual(summary['failed'], failing_resources.__len__())
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertNotIn(unknown_resource, passed_check_resources)
        self.assertNotIn(unknown_resource, failed_check_resources)
        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == '__main__':
    unittest.main()
