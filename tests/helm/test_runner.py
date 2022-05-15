import os
import unittest
from checkov.runner_filter import RunnerFilter
from checkov.helm.runner import Runner


class TestRunnerValid(unittest.TestCase):
    def test_record_relative_path_with_relative_dir(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        checks_allowlist = ['CKV_K8S_42']

        runner = Runner()
        report = runner.run(root_folder=dir_rel_path, runner_filter=RunnerFilter(framework='helm', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        for record in all_checks:
            self.assertIn(record.repo_file_path, record.file_path)


if __name__ == '__main__':
    unittest.main()
