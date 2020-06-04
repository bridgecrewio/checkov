import os
import unittest

from checkov.kubernetes.checks.AllowPrivilegeEscalationPSP import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAllowPrivilegeEscalationPSP(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_PSP"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_summary_skip_check(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_PSP"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(skip_checks=[check.id]))
        for record in report.failed_checks:
            self.assertNotEquals(record.check_id,check.id,"check should be skipped")

if __name__ == '__main__':
    unittest.main()
