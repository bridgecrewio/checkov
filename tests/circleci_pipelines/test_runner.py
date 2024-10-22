import os
import unittest
import pytest

from checkov.circleci_pipelines.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.circleci_pipelines.registry import registry


class TestRunnerValid(unittest.TestCase):

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.CIRCLECI_PIPELINES)

    def test_runner(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        checks = []
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework=['circleci_pipelines'], checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 13)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 32)
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources")
        runner = Runner()
        filter = RunnerFilter(framework=['circleci_pipelines'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.CIRCLECI_PIPELINES: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=filter
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        report.print_console()

@pytest.mark.parametrize(
    "key, expected_key, supported_entities, start_line, end_line",
    [
        (
            'orbs.{orbs: @}.orbs.CKV_CIRCLECIPIPELINES_4[3:6]',
            "orbs",
            ('orbs.{orbs: @}',),
            3, 6
        ),
        (
            'jobs.*.steps[].jobs.*.steps[].CKV_CIRCLECIPIPELINES_7[48:49]',
            "jobs(test-echo).steps[1](checkout)",
            ('jobs.*.steps[]',),
            48, 49
        ),
        (
            'jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}.jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}.CKV_CIRCLECIPIPELINES_2[33:34]',
            'jobs(test-docker-versioned-img).docker.image[1](mongo:2.6.8)',
            ('jobs.*.docker[].{image: image, __startline__: __startline__, __endline__:__endline__}', ),
            33, 34
        )
    ]
)
def test_get_resource(file_path, key, supported_entities, expected_key, start_line, end_line, definition):
    runner = Runner()
    runner.definitions = definition

    new_key = runner.get_resource(file_path, key, supported_entities, start_line, end_line)

    assert new_key == expected_key


if __name__ == "__main__":
    unittest.main()
