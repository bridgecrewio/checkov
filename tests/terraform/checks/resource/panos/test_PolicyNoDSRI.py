import unittest
import os

from checkov.terraform.checks.resource.panos.PolicyNoDSRI import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class PolicyNoDSRI(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_PolicyNoDSRI"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'panos_security_policy.pass1',
            'panos_security_rule_group.pass2',
            'panos_security_policy.pass3',
            'panos_security_rule_group.pass4',
            'panos_security_policy.pass5',
            'panos_security_rule_group.pass6',
        }
        failing_resources = {
            'panos_security_policy.fail1',
            'panos_security_rule_group.fail2',
            'panos_security_policy.fail3',
            'panos_security_rule_group.fail4',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 6)
        self.assertEqual(summary['failed'], 4)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()