import os
import unittest

from checkov.cloudformation.checks.resource.aws.SecurityGroupUnrestrictedIngress22 import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


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

    def test_non_integer_from_port_does_not_crash(self):
        # Regression test: FromPort/ToPort resolving to a non-integer (e.g. an
        # empty string from an unresolved CloudFormation parameter) should not
        # raise ValueError and crash the check. See issue #7669.
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SecurityGroupUnrestrictedIngress22"
        # this should not raise
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        self.assertIsNotNone(report)


if __name__ == '__main__':
    unittest.main()