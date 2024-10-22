import dis
import inspect
import os
import unittest
from collections import defaultdict
from pathlib import Path

from parameterized import parameterized_class

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.runner_filter import RunnerFilter
from checkov.kubernetes.runner import Runner
from checkov.kubernetes.checks.resource.registry import registry

@parameterized_class([
   {"db_connector": NetworkxConnector},
   {"db_connector": RustworkxConnector}
])
class TestRunnerValid(unittest.TestCase):
    def setUp(self) -> None:
        self.orig_checks = registry.checks

    def test_registry_has_type(self):
        self.assertEqual(registry.report_type, CheckType.KUBERNETES)

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        external_checks = os.path.join(current_dir, '..', 'graph', 'checks', 'test_checks')

        runner = Runner(db_connector=self.db_connector())
        filter = RunnerFilter(framework=['kubernetes'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.KUBERNETES: Severities[BcSeverities.OFF]}
        # load the test graph checks because there are no k8s graph checks at the moment, but we need to test that the graph registry knows what type it is
        report = runner.run(root_folder=scan_dir_path, external_checks_dir=[external_checks],
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

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kubernetes'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['kubernetes'], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example.yaml")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework='kubernetes', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example.yaml")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_K8S_21']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework='kubernetes', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_list_metadata_annotations(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "list_annotation", "example.yaml")
        file_rel_path = os.path.relpath(scan_file_path)
        runner = Runner(db_connector=self.db_connector())
        try:
            runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                                runner_filter=RunnerFilter(framework='kubernetes'))
        except Exception:
            self.assertTrue(False, "Could not run K8 runner on configuration")

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "cloudformation", "dockerfile", "helm", "serverless", "terraform", "kustomize"]
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

    def test_parse_with_empty_blocks(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "example_multiple.yaml")
        file_rel_path = os.path.relpath(scan_file_path)
        runner = Runner(db_connector=self.db_connector())
        try:
            report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                       runner_filter=RunnerFilter(framework='kubernetes'))
            # just check that something was parsed and scanned
            self.assertGreater(len(report.failed_checks) + len(report.passed_checks), 0)
        except Exception:
            self.assertTrue(False, "Could not run K8 runner on configuration")

    def test_record_includes_severity(self):
        custom_check_id = "CKV_MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseK8Check):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.KUBERNETES],
                    ["Service"]
                )

            def scan_spec_conf(self, conf):
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['kubernetes'], checks=[custom_check_id])
        )

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_record_check_severity(self):
        custom_check_id = "CKV_MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseK8Check):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.KUBERNETES],
                    ["Service"]
                )

            def scan_spec_conf(self, conf):
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.MEDIUM]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['kubernetes'], checks=['LOW'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_record_check_severity_omit(self):
        custom_check_id = "CKV_MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseK8Check):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.KUBERNETES],
                    ["Service"]
                )

            def scan_spec_conf(self, conf):
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.MEDIUM]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['kubernetes'], checks=['HIGH'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_record_check_skip_severity(self):
        custom_check_id = "CKV_MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseK8Check):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.KUBERNETES],
                    ["Service"]
                )

            def scan_spec_conf(self, conf):
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['kubernetes'], skip_checks=['MEDIUM'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_record_check_skip_severity_omit(self):
        custom_check_id = "CKV_MY_CUSTOM_CHECK"

        registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseK8Check):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.KUBERNETES],
                    ["Service"]
                )

            def scan_spec_conf(self, conf):
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "example.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['kubernetes'], skip_checks=['MEDIUM'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def tearDown(self):
        registry.checks = self.orig_checks
        get_graph_checks_registry("kubernetes").checks = []


if __name__ == '__main__':
    unittest.main()
