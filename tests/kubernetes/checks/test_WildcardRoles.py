import os
import unittest

from checkov.kubernetes.checks.WildcardRoles import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestWildcardRoles(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_WildcardRoles"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'Role.test-should-pass-3.test',
            'Role.test-should-pass-2.test'
        }
        failing_resources = {
            'Role.test-should-fail-1.test',
            'Role.test-should-fail-2.test',
            'ClusterRole.test-should-fail-3.test'
        }

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
