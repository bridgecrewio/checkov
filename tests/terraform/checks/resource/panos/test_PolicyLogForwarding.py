import unittest
import os

from checkov.terraform.checks.resource.panos.PolicyLogForwarding import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestPolicyLogForwarding(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_PolicyLogForwarding"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'panos_security_policy.pass1',
            'panos_security_rule_group.pass2',
            'panos_security_policy.pass3',
            'panos_security_rule_group.pass4',
        }
        failing_resources = {
            'panos_security_policy.fail1',
            'panos_security_rule_group.fail2',
            'panos_security_policy.fail3',
            'panos_security_rule_group.fail4',
            'panos_security_policy.fail5',
            'panos_security_rule_group.fail6',
            'panos_security_policy.fail7',
            'panos_security_rule_group.fail8',
            'panos_security_policy.fail9',
            'panos_security_rule_group.fail10',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 10)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
