import os
import unittest

from checkov.cloudformation.checks.resource.aws.IAMPermissionsManagement import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter

# This test is the same as for IAMPermissionsManagement but uses IAM User test data
# with multiple Policies to ensure that this resource type is tested but it would be
# overkill to use all possible resources for each policy related check

class TestCloudsplainingIAMUser(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/Cloudsplaining_IAMUser"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        self.assertEqual(report.failed_checks[0].check_id, check.id)
        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertEqual(report.failed_checks[0].inspected_key_line, 23)
        self.assertEqual(report.failed_checks[1].inspected_key_line, 35)


if __name__ == '__main__':
    unittest.main()
