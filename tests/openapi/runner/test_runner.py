import os
import unittest
import json

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.output.sarif import Sarif
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
            runner_filter=RunnerFilter(framework=['openapi'], checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 12)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 6)
        self.assertEqual(report.skipped_checks, [])

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
            runner_filter=RunnerFilter(framework=['openapi'])
        )

    def test_pre_validate_non_openapi_file(self) -> None:
        runner = Runner()
        file_content = """
                    '---
            :audit_id: 2018-04-23T224508479Z
            :status_id: 2018-04-23T224508479Z
            :environment: ss-uw1-stg
            :ref: 1.0.0-86-d9c550ede2e6b64ce3b758769e755c2a6584478c
            :repo: email_classifier
            :creator: deploybot
            :task: deployment
            :status: :pending
            :description: \'\'
            '
        """
        result = runner.pre_validate_file(file_content)
        self.assertFalse(result)

    def test_pre_validate_openapi_yaml_file(self) -> None:
        runner = Runner()
        file_content = """
            'openapi: 3.0.0
                info:
                  title: test
                  version: 1.0.0
                security:
                - test: []
                components:
                  securitySchemes:
                  - test:
                      type: http
                      scheme: basic
                '
        """
        result = runner.pre_validate_file(file_content)
        self.assertTrue(result)

    def test_pre_validate_openapi_json_file(self) -> None:
        runner = Runner()
        file_content = json.dumps(
            {
                "openapi": "3.0.0",
                "info": {
                    "title": "test",
                    "version": "1.0.0"
                },
                "components": {
                    "securitySchemes": {
                        "encryptedScheme": {
                            "type": "oauth2"
                        }
                    }
                },
                "paths": {
                    "/": {
                        "get": {
                            "security": [
                                {
                                    "encryptedScheme": [
                                        "write",
                                        "read"
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        )
        result = runner.pre_validate_file(file_content)
        self.assertTrue(result)

    def test_runner_results_consistency(self) -> None:
        current_dir = os.path.dirname(__file__)
        valid_dir_path = os.path.join(current_dir, "resources")
        results_file_path = os.path.join(current_dir, "resources/runner_results/results.sarif")
        runner = Runner()
        checks = ["CKV_OPENAPI_1", "CKV_OPENAPI_4", "CKV_OPENAPI_3"]
        report = runner.run(
            root_folder=valid_dir_path,
            runner_filter=RunnerFilter(framework=['openapi'], checks=checks)
        )
        self.assertEqual(len(report.failed_checks), 12)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(len(report.passed_checks), 6)
        self.assertEqual(report.skipped_checks, [])

        with open(results_file_path) as f:
            expected_report_dict = json.loads(f.read())

        json_sarif_report = Sarif(reports=[report], tool="test").json
        self.assertEqual(len(json_sarif_report["runs"][0]["results"]), len(expected_report_dict["runs"][0]["results"]))


if __name__ == "__main__":
    unittest.main()
