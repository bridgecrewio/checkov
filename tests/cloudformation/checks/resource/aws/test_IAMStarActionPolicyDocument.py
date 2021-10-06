import os
import unittest

from checkov.cloudformation.checks.resource.aws.IAMStarActionPolicyDocument import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestIAMStarActionPolicyDocument(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_IAMStarActionPolicyDocument"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        self.assertEqual(report.failed_checks[0].check_id, check.id)
        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 4)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
