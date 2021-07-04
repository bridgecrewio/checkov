import os
import unittest

from checkov.kubernetes.checks.ApiServerAuditLog import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestApiServerProfiling(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ApiServerAuditLog"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        for failed in report.failed_checks:
            self.assertIn("should-fail", failed.resource)
        for passed in report.passed_checks:
            self.assertIn("should-pass", passed.resource)


if __name__ == '__main__':
    unittest.main()
