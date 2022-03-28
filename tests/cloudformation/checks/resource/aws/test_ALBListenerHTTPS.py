import os
import unittest

from checkov.cloudformation.checks.resource.aws.ALBListenerHTTPS import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestALBListenerHTTPS(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ALBListener"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        unknown_resource = 'AWS::ElasticLoadBalancingV2::Listener.ListenerHTTPUnknown'
        summary = report.get_summary()
        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 7)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertNotIn(unknown_resource, passed_check_resources)
        self.assertNotIn(unknown_resource, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
