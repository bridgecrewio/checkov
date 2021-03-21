
import os
import unittest

from checkov.kubernetes.checks.KubeletKeyFilesSetAppropriate import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestKubeletKeyFilesSetAppropriate(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_KubeletKeyFilesSetAppropriate"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        
        
        for record in report.failed_checks:
            self.assertTrue("FAILED" in record.file_path)
            self.assertTrue(record.check_id in [check.id])
            
        for record in report.passed_checks:
            self.assertTrue("PASSED" in record.file_path)
            self.assertTrue(record.check_id in [check.id])              


if __name__ == '__main__':
    unittest.main()
        
    