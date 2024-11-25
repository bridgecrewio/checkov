import dis
import inspect
import os
import unittest
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.runner_filter import RunnerFilter
from checkov.arm.runner import Runner
from checkov.arm.registry import arm_resource_registry, arm_parameter_registry

RESOURCES_DIR = Path(__file__).parent / "resources"


class TestRunnerValid(unittest.TestCase):

    def setUp(self) -> None:
        self.orig_checks = arm_resource_registry.checks

    def test_registry_has_type(self):
        self.assertEqual(arm_resource_registry.report_type, CheckType.ARM)
        self.assertEqual(arm_parameter_registry.report_type, CheckType.ARM)

    def test_runner_honors_enforcement_rules(self):
        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        runner = Runner()
        filter = RunnerFilter(framework=['arm'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.ARM: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=scan_dir_path, external_checks_dir=None, runner_filter=filter)

        # then
        summary = report.get_summary()

        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["skipped"] == 0
        assert summary["parsing_errors"] == 0

    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ['CKV_AZURE_18']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='arm', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ['CKV_AZURE_18']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='arm', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            file_name = record.file_path.split('/')[-1]
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}/{file_name}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example.json")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_AZURE_18']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework='arm', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example.json")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_AZURE_18']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework='arm', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_wrong_check_imports(self):
        wrong_imports = ["cloudformation", "dockerfile", "helm", "kubernetes", "serverless", "terraform"]
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

    def test_record_includes_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        arm_resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["Microsoft.Web/sites"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.json")

        report = Runner().run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['arm'], checks=[custom_check_id])
        )

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_severity_check_filter_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        arm_resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["Microsoft.Web/sites"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        checks_allowlist = ['MEDIUM']
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.json")

        report = Runner().run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['arm'], checks=checks_allowlist)
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_check_filter_include(self):

        custom_check_id = "MY_CUSTOM_CHECK"

        arm_resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["Microsoft.Web/sites"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        checks_allowlist = ['MEDIUM']
        check.severity = Severities[BcSeverities.HIGH]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.json")

        report = Runner().run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['arm'], checks=checks_allowlist)
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_skip_check_filter_omit(self):

        custom_check_id = "MY_CUSTOM_CHECK"
        arm_resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["Microsoft.Web/sites"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        checks_denylist = ['MEDIUM']
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.json")

        report = Runner().run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['arm'], skip_checks=checks_denylist)
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_skip_check_filter_include(self):

        custom_check_id = "MY_CUSTOM_CHECK"
        arm_resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["Microsoft.Web/sites"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        checks_denylist = ['MEDIUM']
        check.severity = Severities[BcSeverities.HIGH]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.json")

        report = Runner().run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['arm'], skip_checks=checks_denylist)
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_invalid_file_raises_no_exception(self):
        # given
        test_file_path = RESOURCES_DIR / "invalid.json"

        # when
        report = Runner().run(files=[str(test_file_path)])

        # then
        summary = report.get_summary()

        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["skipped"] == 0
        assert summary["parsing_errors"] == 0

    def test_no_resource_raises_no_exception(self):
        # given
        test_file_path = RESOURCES_DIR / "no_resource.json"

        # when
        report = Runner().run(files=[str(test_file_path)])

        # then
        summary = report.get_summary()

        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["skipped"] == 0
        assert summary["parsing_errors"] == 0

    def tearDown(self):
        arm_resource_registry.checks = self.orig_checks


if __name__ == '__main__':
    unittest.main()
