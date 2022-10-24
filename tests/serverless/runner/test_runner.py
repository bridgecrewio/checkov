import dis
import inspect
import os
import unittest
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

from checkov.cloudformation.checks.resource.aws import *  # noqa - prevent circular import
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.serverless.checks.function.base_function_check import BaseFunctionCheck
from checkov.serverless.runner import Runner
from checkov.serverless.checks.function.registry import function_registry
from checkov.serverless.checks.provider.registry import provider_registry
from checkov.serverless.checks.complete.registry import complete_registry
from checkov.serverless.checks.custom.registry import custom_registry
from checkov.serverless.checks.layer.registry import layer_registry
from checkov.serverless.checks.package.registry import package_registry
from checkov.serverless.checks.plugin.registry import plugin_registry
from checkov.serverless.checks.service.registry import service_registry


class TestRunnerValid(unittest.TestCase):

    def setUp(self) -> None:
        self.orig_checks = function_registry.checks

    def test_registry_has_type(self):
        self.assertEqual(function_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(provider_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(complete_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(custom_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(layer_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(package_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(plugin_registry.report_type, CheckType.SERVERLESS)
        self.assertEqual(service_registry.report_type, CheckType.SERVERLESS)

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        runner = Runner()
        filter = RunnerFilter(framework=['serverless'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.SERVERLESS: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=scan_dir_path, external_checks_dir=None,
                            runner_filter=filter)

        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ['CKV_AWS_49']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='serverless', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ['CKV_AWS_49']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='serverless', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yml")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_AWS_49']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework='serverless', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yml")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_AWS_49']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework='serverless', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "cloudformation", "dockerfile", "helm", "kubernetes", "terraform"]
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

    def test_provider_function_att_type_mismatch(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yaml")
        file_abs_path = os.path.abspath(scan_file_path)

        report = runner.run(files=[file_abs_path], runner_filter=RunnerFilter(framework='serverless'), root_folder="")
        self.assertEqual(0, len(report.parsing_errors))
        self.assertLess(0, len(report.passed_checks + report.failed_checks))

    def test_record_includes_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"


        function_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseFunctionCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["serverless_aws"]
                )

            def scan_function_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yaml")
        file_abs_path = os.path.abspath(scan_file_path)

        report = Runner().run(files=[file_abs_path], runner_filter=RunnerFilter(framework=['serverless'], checks=[custom_check_id]), root_folder="")

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_record_check_severity_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"


        function_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseFunctionCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["serverless_aws"]
                )

            def scan_function_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yaml")
        file_abs_path = os.path.abspath(scan_file_path)

        report = Runner().run(files=[file_abs_path], runner_filter=RunnerFilter(framework=['serverless'], checks=['MEDIUM']), root_folder="")

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_record_check_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"


        function_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseFunctionCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["serverless_aws"]
                )

            def scan_function_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yaml")
        file_abs_path = os.path.abspath(scan_file_path)

        report = Runner().run(files=[file_abs_path], runner_filter=RunnerFilter(framework=['serverless'], checks=['MEDIUM']), root_folder="")

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_record_check_skip_severity_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        function_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseFunctionCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["serverless_aws"]
                )

            def scan_function_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yaml")
        file_abs_path = os.path.abspath(scan_file_path)

        report = Runner().run(files=[file_abs_path], runner_filter=RunnerFilter(framework=['serverless'], skip_checks=['MEDIUM']), root_folder="")

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_record_check_skip_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        function_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseFunctionCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["serverless_aws"]
                )

            def scan_function_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "serverless.yaml")
        file_abs_path = os.path.abspath(scan_file_path)

        report = Runner().run(files=[file_abs_path], runner_filter=RunnerFilter(framework=['serverless'], skip_checks=['MEDIUM']), root_folder="")

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def tearDown(self):
        function_registry.checks = self.orig_checks


if __name__ == '__main__':
    unittest.main()
