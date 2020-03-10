import os
import unittest

from checkov.cloudformation.checks.resource.aws.ECRPolicy import check
from checkov.cloudformation.runner import Runner


class TestECRPolicy(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ECRPolicy"
        report = runner.run(root_folder=test_files_dir).get_new_report_for_check_id(check.id)
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
