import os
import unittest
from unittest import mock

from checkov.gitlab.runner import Runner
from checkov.runner_filter import RunnerFilter


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


if __name__ == "__main__":
    unittest.main()
