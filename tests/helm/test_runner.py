import os
import unittest

from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter
from checkov.helm.runner import Runner
from tests.helm.utils import helm_exists


class TestRunnerValid(unittest.TestCase):
    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_record_relative_path_with_relative_dir(self):
        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "infrastructure")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace("\\", "/")

        checks_allowlist = ["CKV_K8S_42"]

        runner = Runner()
        report = runner.run(
            root_folder=dir_rel_path, runner_filter=RunnerFilter(framework=["helm"], checks=checks_allowlist)
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.check_type, CheckType.HELM)
        for record in all_checks:
            self.assertIn(record.repo_file_path, record.file_path)
        for resource in report.resources:
            self.assertIn('/helm-tiller/pwnchart/templates', resource)

    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "infrastructure")

        runner = Runner()
        filter = RunnerFilter(framework=['helm'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.HELM: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=scan_dir_path, runner_filter=filter
        )

        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        
    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_runner_invalid_chart(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "schema-registry")

        runner = Runner()
        filter = RunnerFilter(framework=['helm'], use_enforcement_rules=False)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        report = runner.run(
            root_folder=scan_dir_path, runner_filter=filter
        )

        self.assertEqual(len(report.failed_checks), 0)

    @unittest.skipIf(not helm_exists(), "helm not installed")
    def test_get_binary_output_from_directory_equals_to_get_binary_result(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "runner", "resources", "schema-registry")

        runner_filter = RunnerFilter(framework=['helm'], use_enforcement_rules=False)

        chart_meta = Runner.parse_helm_chart_details(scan_dir_path)
        chart_item = (scan_dir_path, chart_meta)
        regular_result = Runner.get_binary_output(chart_item, target_dir='./tmp', helm_command="helm",
                                                  runner_filter=runner_filter)
        result_from_directory = Runner.get_binary_output_from_directory(str(scan_dir_path),
                                                                        target_dir='./tmp', helm_command="helm",
                                                                        runner_filter=runner_filter)
        assert regular_result == result_from_directory


if __name__ == "__main__":
    unittest.main()
