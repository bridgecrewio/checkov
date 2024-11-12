import dis
import inspect
import unittest

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

from parameterized import parameterized_class

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.dockerfile.base_dockerfile_check import BaseDockerfileCheck
from checkov.dockerfile.runner import Runner, get_files_definitions
from checkov.dockerfile.registry import registry
from checkov.runner_filter import RunnerFilter

RESOURCES_DIR = Path(__file__).parent / "resources"

@parameterized_class([
   {"db_connector": NetworkxConnector},
   {"db_connector": RustworkxConnector}
])
class TestRunnerValid(unittest.TestCase):
    def setUp(self) -> None:
        self.orig_checks = registry.checks

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.DOCKERFILE)

    def test_runner_empty_dockerfile(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/empty_dockerfile"
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all'))
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_runner_name_variations(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/name_variations"
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all'))
        self.assertEqual(len(report.resources), 2)
        self.assertEqual(len([file for file in report.resources if 'Dockerfile.prod' in file]), 1)
        self.assertEqual(len([file for file in report.resources if 'prod.dockerfile' in file]), 1)

    def test_runner_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all',checks=['CKV_DOCKER_1']))
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/fail"
        runner = Runner(db_connector=self.db_connector())
        filter = RunnerFilter(framework=['dockerfile'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.DOCKERFILE: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=filter)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)

    def test_runner_failing_check_with_file_path(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_file_path = current_dir + "/resources/expose_port/fail/Dockerfile"
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(
            files=[valid_file_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all", checks=["CKV_DOCKER_1"]),
        )
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])

    def test_runner_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/expose_port/pass"
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["all"],checks=["CKV_DOCKER_1", "CKV2_DOCKER_1"]))
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])

        #  also check the abs file paths
        record_python = next(check for check in report.passed_checks if check.check_id == "CKV_DOCKER_1")
        assert record_python.file_abs_path.endswith("tests/dockerfile/resources/expose_port/pass/Dockerfile")
        record_graph = next(check for check in report.passed_checks if check.check_id == "CKV2_DOCKER_1")
        assert record_graph.file_abs_path.endswith("tests/dockerfile/resources/expose_port/pass/Dockerfile")

    def test_runner_skip_check(self):
        #  given
        valid_dir_path = Path(__file__).parent / "resources/expose_port/skip"

        # when
        report = Runner(db_connector=self.db_connector()).run(
            root_folder=str(valid_dir_path),
            external_checks_dir=None,
            runner_filter=RunnerFilter(
                framework=["dockerfile"],
                checks=["CKV_DOCKER_1", "CKV_DOCKER_5", "CKV_DOCKER_9", "CKV2_DOCKER_7"],
            ),
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["skipped"], 3)
        self.assertEqual(summary["parsing_errors"], 0)

        expected_skipped_cehcks = [record.check_id for record in report.skipped_checks]
        self.assertCountEqual(["CKV_DOCKER_1", "CKV_DOCKER_5", "CKV2_DOCKER_7"], expected_skipped_cehcks)

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
        runner = Runner(db_connector=self.db_connector())
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
        runner = Runner(db_connector=self.db_connector())
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
        runner = Runner(db_connector=self.db_connector())
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
        runner = Runner(db_connector=self.db_connector())
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
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='dockerfile', skip_checks=['MEDIUM']))

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_skip_wildcard_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/wildcard_skip"
        runner = Runner(db_connector=self.db_connector())
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

    def test_runner_extra_resources(self):
        # given
        test_file = RESOURCES_DIR / "name_variations/Dockerfile.prod"

        # when
        report = Runner(db_connector=self.db_connector()).run(
            files=[str(test_file)],
            runner_filter=RunnerFilter(framework=['dockerfile'], checks=["CKV_DOCKER_4"])  # chose a check, which will find nothing
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 1)

        self.assertEqual(len(report.extra_resources), 1)
        extra_resource = next(iter(report.extra_resources))
        self.assertEqual(extra_resource.file_abs_path, str(test_file))
        self.assertTrue(extra_resource.file_path.endswith("Dockerfile.prod"))

    def test_runner_multi_line(self):
        # given
        test_file = RESOURCES_DIR / "multiline_command/"

        # when
        report = Runner(db_connector=self.db_connector()).run(
            files=[str(test_file)],
            runner_filter=RunnerFilter(framework=['dockerfile'], checks=["CKV_DOCKER_9"])  # chose a check, which will find nothing
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 1)

        self.assertEqual(len(report.extra_resources), 1)
        extra_resource = next(iter(report.extra_resources))
        self.assertEqual(extra_resource.file_abs_path, str(test_file))
        self.assertTrue(extra_resource.file_path.endswith("Dockerfile"))


    def tearDown(self) -> None:
        registry.checks = self.orig_checks


if __name__ == '__main__':
    unittest.main()
