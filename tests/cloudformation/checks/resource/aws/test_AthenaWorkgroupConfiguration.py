import os
import unittest

from checkov.cloudformation.checks.resource.aws.AthenaWorkgroupConfiguration import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAthenaWorkgroupConfiguration(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # There is some internal conflicts on "Tags" in the Athena WG Docs. And corresponding specs.
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-athena-workgroup.html
        # This may mean that the "Tags" in this test data needs to correspondingly change when CF / CF Lint are updated in the future.
        # CF Lint Issue: https://github.com/aws-cloudformation/cfn-python-lint/issues/1577
        test_files_dir = current_dir + "/example_AthenaWorkgroupConfiguration"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
