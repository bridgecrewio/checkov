import os
import unittest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.gitlab_ci.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.gitlab_ci.checks.registry import registry


class TestRunnerValid(unittest.TestCase):

    def test_runner(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        checks = ["CKV_GITLABCI_1", "CKV_GITLABCI_2"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework=['gitlab_ci'], checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 5)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 9)
        self.assertEqual(len(report.skipped_checks), 1)
        report.print_console()

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        filter = RunnerFilter(framework=['gitlab_ci'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.GITLAB_CI: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=filter
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.GITLAB_CI)

    def test_runner_image_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework=['gitlab_ci'], checks=['CKV_GITLABCI_3'])
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 8)
        self.assertEqual(report.skipped_checks, [])

    def test_runner_image_resources(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources/resource_images")
        runner = Runner()
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework=['gitlab_ci'], checks=['CKV_GITLABCI_3'])
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 4)
        self.assertEqual(report.skipped_checks, [])
        self.assertEqual(report.passed_checks[0].resource, 'prebuild')
        self.assertEqual(report.passed_checks[1].resource, 'build.image')
        self.assertEqual(report.passed_checks[2].resource, 'deploy')
        self.assertEqual(report.passed_checks[3].resource, 'deploy')


if __name__ == "__main__":
    unittest.main()
