import os
import unittest

from checkov.cloudformation.checks.resource.aws.SecurityGroupUnrestrictedIngress22 import check
from checkov.cloudformation.runner import Runner
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter


def _ingress_conf(from_port, to_port):
    return {
        'Type': 'AWS::EC2::SecurityGroup',
        'Properties': {
            'SecurityGroupIngress': [
                {'FromPort': from_port, 'ToPort': to_port, 'CidrIp': '0.0.0.0/0'}
            ]
        },
    }


class TestSecurityGroupUnrestrictedIngress22(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SecurityGroupUnrestrictedIngress22"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_unresolvable_port_is_unknown(self):
        # A Ref to a parameter with an empty Default resolves to ''. Before,
        # int('') raised inside range() and the resource got no result at all.
        self.assertEqual(check.scan_resource_conf(_ingress_conf('', '22')), CheckResult.UNKNOWN)
        self.assertEqual(check.scan_resource_conf(_ingress_conf('22', 'not-a-port')), CheckResult.UNKNOWN)

    def test_valid_ports_are_unaffected(self):
        self.assertEqual(check.scan_resource_conf(_ingress_conf('20', '25')), CheckResult.FAILED)
        self.assertEqual(check.scan_resource_conf(_ingress_conf(20, 25)), CheckResult.FAILED)
        # Inverted range stays PASSED, matching SecurityGroupRangeInvalid-PASSED.yaml.
        self.assertEqual(check.scan_resource_conf(_ingress_conf('23', '21')), CheckResult.PASSED)

    def test_unparseable_rule_does_not_mask_failed_sibling(self):
        # A single unparseable rule must not hide a definitive FAILED verdict on
        # a sibling rule. Copilot flagged this regression in the original PR.
        conf = {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'SecurityGroupIngress': [
                    {'FromPort': '', 'ToPort': '', 'CidrIp': '10.0.0.0/8'},
                    {'FromPort': 22, 'ToPort': 22, 'CidrIp': '0.0.0.0/0'},
                ]
            },
        }
        self.assertEqual(check.scan_resource_conf(conf), CheckResult.FAILED)

    def test_all_rules_unparseable_still_returns_unknown(self):
        # If every rule is unparseable, no rule speaks, so UNKNOWN is correct.
        conf = {
            'Type': 'AWS::EC2::SecurityGroup',
            'Properties': {
                'SecurityGroupIngress': [
                    {'FromPort': '', 'ToPort': '', 'CidrIp': '10.0.0.0/8'},
                    {'FromPort': '', 'ToPort': '', 'CidrIp': '10.0.0.0/8'},
                ]
            },
        }
        self.assertEqual(check.scan_resource_conf(conf), CheckResult.UNKNOWN)


if __name__ == '__main__':
    unittest.main()
