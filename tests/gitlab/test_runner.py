import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.gitlab.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.gitlab.registry import registry


class TestGitlabRunnerValid(unittest.TestCase):

    @mock.patch.dict(os.environ, {"CKV_GITLAB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_object_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "gitlab_conf", "fail")
        runner = Runner()
        runner.gitlab.gitlab_conf_dir_path = valid_dir_path

        checks = ["CKV_GITLAB_1", "CKV_GITLAB_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITLAB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "gitlab_conf", "fail")
        runner = Runner()
        runner.gitlab.gitlab_conf_dir_path = valid_dir_path
        filter = RunnerFilter(framework=['gitlab_configuration'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.GITLAB_CONFIGURATION: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=filter
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    @mock.patch.dict(os.environ, {"CKV_GITLAB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_object_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "gitlab_conf", "pass")
        runner = Runner()
        runner.gitlab.gitlab_conf_dir_path = valid_dir_path
        checks = ["CKV_GITLAB_1", "CKV_GITLAB_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITLAB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_files_ignore(self):
        # given
        test_file = Path(__file__).parent / "resources/gitlab_conf/pass/merge_request_approval_conf.json"
        checks = ["CKV_GITLAB_1", "CKV_GITLAB_2"]

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

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.GITLAB_CONFIGURATION)


if __name__ == "__main__":
    unittest.main()
