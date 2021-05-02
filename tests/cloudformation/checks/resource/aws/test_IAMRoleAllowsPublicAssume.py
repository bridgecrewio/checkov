import os
import unittest

from checkov.cloudformation.checks.resource.aws.IAMRoleAllowsPublicAssume import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestIAMRoleAllowsPublicAssume(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_IAMRoleAllowsPublicAssume"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        for record in report.failed_checks:
            self.assertEqual(record.check_id, check.id)
        
        for record in report.passed_checks:
            self.assertEqual(record.check_id, check.id)

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
