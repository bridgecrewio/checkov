import os
import unittest
from unittest import mock

from checkov.serverless.checks.function.aws.AdminPolicyDocument import check
from checkov.serverless.runner import Runner
from checkov.runner_filter import RunnerFilter

class TestAdminPolicyDocument(unittest.TestCase):

    @mock.patch.dict(os.environ, {"sneaky_var": "*"})
    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_AdminPolicyDocument"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 2,
                         f"Passed checks: {[fc.file_path for fc in report.passed_checks]}")
        self.assertEqual(summary['failed'], 6,
                         f"Failed checks: {[fc.file_path for fc in report.failed_checks]}")
        self.assertEqual(summary['skipped'], 0,
                         f"Skipped checks: {[fc.file_path for fc in report.skipped_checks]}")
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
