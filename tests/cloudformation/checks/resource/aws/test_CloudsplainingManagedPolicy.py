import os
import unittest

from checkov.cloudformation.checks.resource.aws.IAMPermissionsManagement import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter

# This test is the same as for IAMPermissionsManagement but uses 'ManagedPolicy' test data
# instead of 'Policy' data. This is to ensure some ManagedPolicy tests are excercised
# because it would be overkill to duplicate every test with both.

class TestCloudsplainingManagedPolicy(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/Cloudsplaining_ManagedPolicy"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        self.assertEqual(report.failed_checks[0].check_id, check.id)
        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertEqual(report.failed_checks[0].inspected_key_line, 13)
        self.assertEqual(report.failed_checks[1].inspected_key_line, 28)
        self.assertEqual(report.failed_checks[2].inspected_key_line, 43)


if __name__ == '__main__':
    unittest.main()
