import os
import unittest
from pathlib import Path
from unittest import mock

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.github.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.github.registry import registry


class TestRunnerValid(unittest.TestCase):

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.GITHUB_CONFIGURATION)

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1",
                                  "GITHUB_REF": "refs/heads/feature-branch-1"}, clear=True)
    def test_runner_webhooks_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "webhooks")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = ["CKV_GITHUB_6", "CKV_GITHUB_7"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1",
                                  "GITHUB_REF": "refs/heads/feature-branch-1"}, clear=True)
    def test_runner_object_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "fail")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = ["CKV_GITHUB_1", "CKV_GITHUB_2", "CKV_GITHUB_3"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(runner.github.current_branch, "feature-branch-1")
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1",
                                  "GITHUB_REF": "refs/heads/feature-branch-1"}, clear=True)
    def test_runner_object_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "fail")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path
        filter = RunnerFilter(framework=['github_configuration'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.GITHUB_CONFIGURATION: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=filter
        )
        self.assertEqual(runner.github.current_branch, "feature-branch-1")
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_repo_security(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "repo")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = [
            "CKV_GITHUB_4",
            "CKV_GITHUB_5",
            "CKV_GITHUB_8",
            "CKV_GITHUB_10",
            "CKV_GITHUB_11",
            "CKV_GITHUB_12",
            "CKV_GITHUB_13",
            "CKV_GITHUB_14",
            "CKV_GITHUB_15",
            "CKV_GITHUB_16",
            "CKV_GITHUB_17",
            "CKV_GITHUB_18",
        ]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 4)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 7)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_repo_admin_collaborators(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "collaborators")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = ["CKV_GITHUB_9"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_empty_repo_collaborators(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "empty_collabs")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = ["CKV_GITHUB_9"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_repo_security_no_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "repo_no_rules")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = ["CKV_GITHUB_4", "CKV_GITHUB_5"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_object_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources", "github_conf", "pass")
        runner = Runner()
        runner.github.github_conf_dir_path = valid_dir_path

        checks = ["CKV_GITHUB_1", "CKV_GITHUB_2", "CKV_GITHUB_3"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(report.skipped_checks, [])

    @mock.patch.dict(os.environ, {"CKV_GITHUB_CONFIG_FETCH_DATA": "False", "PYCHARM_HOSTED": "1"}, clear=True)
    def test_runner_files_ignore(self):
        # given
        test_file = Path(__file__).parent / "resources/github_conf/pass/org_security.json"
        checks = ["CKV_GITHUB_1", "CKV_GITHUB_2", "CKV_GITHUB_3"]

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
