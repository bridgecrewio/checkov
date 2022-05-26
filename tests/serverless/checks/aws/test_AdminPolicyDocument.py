import os
import unittest

from checkov.serverless.checks.function.aws.AdminPolicyDocument import check
from checkov.serverless.runner import Runner
from checkov.runner_filter import RunnerFilter

class TestAdminPolicyDocument(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Used in
        os.environ["sneaky_var"] = "*"

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
