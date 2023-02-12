import os
import unittest
from pathlib import Path

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.kustomize.runner import Runner
from tests.kustomize.utils import kustomize_exists


class TestRunnerValid(unittest.TestCase):
    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "example")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        filter = RunnerFilter(framework=['kustomize'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.KUSTOMIZE: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=filter)

        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_relative_dir(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "example")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        checks_allowlist = ['CKV_K8S_37']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')
            assert record.file_path.startswith(('/base', '/overlays'))

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_direct_oberlay(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        scan_dir_path = Path(__file__).parent / "runner/resources/example/overlays/dev"


        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        checks_allowlist = ['CKV_K8S_37']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertNotEqual(record.file_path, record.file_abs_path)
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_direct_prod2_oberlay(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        scan_dir_path = Path(__file__).parent / "runner/resources/example/overlays/prod-2"


        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        checks_allowlist = ['CKV_K8S_37']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertNotEqual(record.file_path, record.file_abs_path)
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')
    
    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_no_file_type_exists(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        scan_dir_path = Path(__file__).parent / "runner/resources/example/no_type"


        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertEqual(len(all_checks), 0)  # we should no get any results


if __name__ == '__main__':
    unittest.main()
