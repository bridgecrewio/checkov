import dis
import inspect
import os
import unittest
from pathlib import Path
from typing import Dict, Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.runner_filter import RunnerFilter
from checkov.kustomize.runner import Runner
from checkov.common.output.report import Report

class TestRunnerValid(unittest.TestCase):

    def test_record_relative_path_with_relative_dir(self):
        @unittest.skipIf(os.name == "nt", "Skipping Kustomize test for windows OS.")
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ['CKV_K8S_37']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='kustomize', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # Kustomize deals with absolute paths
            #self.assertEqual(record.repo_file_path in record.file_path)
            self.assertIn(record.repo_file_path, record.file_path)

if __name__ == '__main__':
    unittest.main()
