import os
import unittest
from unittest import mock

from checkov.bitbucket.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
