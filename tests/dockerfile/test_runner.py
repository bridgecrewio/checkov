import dis
import inspect
import unittest

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck
from checkov.dockerfile.runner import Runner, get_files_definitions
from checkov.dockerfile.registry import registry
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def setUp(self) -> None:
        self.orig_checks = registry.checks

    def test_runner_empty_dockerfile(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/empty_dockerfile"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all'))
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()
    
    def test_runner_name_variations(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/name_variations"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all'))
        self.assertEqual(len(report.resources), 2)
        self.assertEqual(len([file for file in report.resources if 'Dockerfile.prod' in file]), 1)
        self.assertEqual(len([file for file in report.resources if 'prod.dockerfile' in file]), 1)
        report.print_console()

    def test_runner_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_failing_check_with_file_path(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_file_path = current_dir + "/resources/expose_port/fail/Dockerfile"
        runner = Runner()
        report = runner.run(
            files=[valid_file_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all", checks=["CKV_DOCKER_1"]),
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/pass"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_skip_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/skip"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.passed_checks, [])
        report.print_console()

    def test_record_has_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseDockerfileCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["RUN"]
                )

            def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str):
                return CheckResult.FAILED, conf[0]

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='dockerfile', checks=[custom_check_id]))

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_runner_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseDockerfileCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["RUN"]
                )

            def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str):
                return CheckResult.FAILED, conf[0]

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='dockerfile', checks=['MEDIUM']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_runner_severity_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseDockerfileCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["RUN"]
                )

            def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str):
                return CheckResult.FAILED, conf[0]

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='dockerfile', checks=['CRITICAL']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_runner_skip_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseDockerfileCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["RUN"]
                )

            def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str):
                return CheckResult.FAILED, conf[0]

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='dockerfile', checks=['MEDIUM']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_runner_skip_severity_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseDockerfileCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["RUN"]
                )

            def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str):
                return CheckResult.FAILED, conf[0]

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='dockerfile', skip_checks=['MEDIUM']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_skip_wildcard_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/wildcard_skip"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['dockerfile']))
        self.assertEqual(len(report.skipped_checks), 1)
        self.assertGreaterEqual(len(report.passed_checks), 1)
        self.assertGreaterEqual(len(report.failed_checks), 2)

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "cloudformation", "helm", "kubernetes", "serverless", "terraform"]
        check_imports = []

        checks_path = Path(inspect.getfile(Runner)).parent.joinpath("checks")
        for file in checks_path.rglob("*.py"):
            with file.open() as f:
                instructions = dis.get_instructions(f.read())
                import_names = [instr.argval for instr in instructions if "IMPORT_NAME" == instr.opname]

                for import_name in import_names:
                    wrong_import = next((import_name for x in wrong_imports if x in import_name), None)
                    if wrong_import:
                        check_imports.append({file.name: wrong_import})

        assert len(check_imports) == 0, f"Wrong imports were added: {check_imports}"

    def test_get_files_definitions(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dockerfile = current_dir + "/resources/name_variations/Dockerfile.prod"
        not_valid_dockerfile = current_dir + "/resources/not_dockerfile/dockerfile.png"
        results = get_files_definitions([valid_dockerfile, not_valid_dockerfile])
        assert len(results) == 2
        assert len(results[0]) == 1 and list(results[0].keys())[0] == valid_dockerfile
        assert len(results[1]) == 1 and list(results[1].keys())[0] == valid_dockerfile


    def tearDown(self) -> None:
        registry.checks = self.orig_checks



if __name__ == '__main__':
    unittest.main()
