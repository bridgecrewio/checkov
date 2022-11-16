import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.bitbucket.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.bitbucket.registry import registry


class TestRunnerValid(unittest.TestCase):

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.BITBUCKET_CONFIGURATION)

    @mock.patch.dict(os.environ, {"CKV_BITBUCKET_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1",
                                  "BITBUCKET_REPO_FULL_NAME": "shaharsamira/terragoat2"}, clear=True)
    def test_runner_object_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "bitbucket_conf", "fail")
        runner = Runner()
        runner.bitbucket.bitbucket_conf_dir_path = valid_dir_path

        checks = ["CKV_BITBUCKET_1"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.skipped_checks, [])

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "bitbucket_conf", "fail")
        runner = Runner()
        filter = RunnerFilter(framework=['bitbucket_configuration'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.BITBUCKET_CONFIGURATION: Severities[BcSeverities.OFF]}
        runner.bitbucket.bitbucket_conf_dir_path = valid_dir_path

        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=filter
        )
        summary = report.get_summary()

        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["skipped"] == 0
        assert summary["parsing_errors"] == 0

    @mock.patch.dict(os.environ, {"CKV_BITBUCKET_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_object_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "bitbucket_conf", "pass")
        runner = Runner()
        runner.bitbucket.bitbucket_conf_dir_path = valid_dir_path

        checks = ["CKV_BITBUCKET_1"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_BITBUCKET_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_files_ignore(self):
        # given
        test_file = Path(__file__).parent / "resources/bitbucket_conf/pass/branch_restrictions.json"
        checks = ["CKV_BITBUCKET_1"]

        # when
        report = Runner().run(
            files=[str(test_file)],
            runner_filter=RunnerFilter(checks=checks)
        )

        # then
        # even it points to a file with scannable content, it should skip it
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.skipped_checks), 0)


if __name__ == "__main__":
    unittest.main()
