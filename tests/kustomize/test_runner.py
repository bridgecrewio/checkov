import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.kustomize.runner import Runner
from tests.kustomize.utils import kustomize_exists


def _setup_test_under_example():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    scan_dir_path = os.path.join(current_dir, "runner", "resources", "example")
    # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
    dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')
    runner = Runner()
    runner.templateRendererCommand = "kustomize"
    runner.templateRendererCommandOptions = "build"
    checks_allowlist = ['CKV_K8S_37']
    return checks_allowlist, dir_rel_path, runner


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
        checks_allowlist, dir_rel_path, runner = _setup_test_under_example()
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')
            assert record.file_path.startswith(('/base', '/overlays'))

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_record_relative_path_with_relative_dir_with_origin_annotations(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        with mock.patch.dict(os.environ, {"CHECKOV_ALLOW_KUSTOMIZE_FILE_EDITS": "True"}):
            checks_allowlist, dir_rel_path, runner = _setup_test_under_example()
            report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertIn(record.file_path, record.file_abs_path)
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')
            assert record.file_path.startswith(('/base', '/overlays'))
            assert record.caller_file_path == '/base/deployment.yaml' or record.caller_file_path == '/deployment.yaml'
            assert record.caller_file_line_range == (2, 24)

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

    @unittest.skipIf(os.name == "nt" or not kustomize_exists(), "kustomize not installed or Windows OS")
    def test_get_binary_output_from_directory_equals_to_get_binary_result(self):
        scan_dir_path = Path(__file__).parent / "runner/resources/example/no_type"
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')
        runner = Runner()
        runner.templateRendererCommand = "kustomize"
        runner.templateRendererCommandOptions = "build"

        # Runs the runner fully just to build `runner.kustomizeProcessedFolderAndMeta`
        _ = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kustomize']))
        regular_result = runner.get_binary_output(str(scan_dir_path), runner.kustomizeProcessedFolderAndMeta,
                                                  runner.templateRendererCommand)
        result_from_directory = runner.get_binary_output_from_directory(str(scan_dir_path),
                                                                        runner.templateRendererCommand)
        assert regular_result == result_from_directory



if __name__ == '__main__':
    unittest.main()
