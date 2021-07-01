import os
import unittest

from checkov.kubernetes.checks.ApiServerNodeRestrictionPlugin import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestApiServerNodeRestrictionPlugin(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ApiServerNodeRestrictionPlugin"

        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        
        for record in report.failed_checks:
            self.assertIn("FAILED", record.file_path)
            self.assertIn(record.check_id, [check.id])
            
        for record in report.passed_checks:
            self.assertIn("PASSED", record.file_path)
            self.assertIn(record.check_id, [check.id])


if __name__ == '__main__':
    unittest.main()
