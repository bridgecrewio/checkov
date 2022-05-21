import os
import unittest

from checkov.cloudformation.checks.resource.aws.ALBDropHttpHeaders import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestALBDropHttpHeaders(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_ALBDropHttpHeaders"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        for record in report.failed_checks:
            self.assertEqual(record.check_id, check.id)

        for record in report.passed_checks:
            self.assertEqual(record.check_id, check.id)

        passing_resources = {
            "AWS::ElasticLoadBalancingV2::LoadBalancer.PassDefaultType",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.PassDefaultTypeBool",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.PassExplicitALB",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.PassMultipleAttributes",
        }

        failing_resources = {
            "AWS::ElasticLoadBalancingV2::LoadBalancer.FailDefaultType",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.FailExplicitALB",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.FailExplicitFalse",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.FailExplicitFalse2",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.FailKeyNotExist",
            "AWS::ElasticLoadBalancingV2::LoadBalancer.FailKeyNotExist2",
        }

        # 2 Unknown resources are tested which are properly silently ignored

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 6)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
