import os
import unittest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.openapi.checks.registry import openapi_registry

class TestRunnerValid(unittest.TestCase):

    def test_runner(self) -> None:
        current_dir = os.path.dirname(__file__)
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        checks = ["CKV_OPENAPI_1", "CKV_OPENAPI_4", "CKV_OPENAPI_3"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework='openapi', checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 12)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 6)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_honors_enforcement_rules(self) -> None:
        current_dir = os.path.dirname(__file__)
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        filter = RunnerFilter(framework=['openapi'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.OPENAPI: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=filter
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    def test_registry_has_type(self):
        self.assertEqual(openapi_registry.report_type, CheckType.OPENAPI)

    def test_runner_all_checks(self) -> None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework='openapi')
        )
        report.print_console()


if __name__ == "__main__":
    unittest.main()