import os
import unittest

from checkov.arm.checks.resource.StorageAccountMinimumTlsVersion import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestStorageAccountMinimumTlsVersion(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_StorageAccountMinimumTlsVersion"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 3)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()
