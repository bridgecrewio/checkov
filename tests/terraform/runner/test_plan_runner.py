import itertools
import os
import unittest
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any
from unittest import mock

from parameterized import parameterized_class

# do not remove - prevents circular import
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform import TFDefinitionKey
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.plan_runner import Runner, resource_registry


@parameterized_class([
    {"db_connector": NetworkxConnector},
    {"db_connector": RustworkxConnector},
])
class TestRunnerValid(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orig_checks = deepcopy(resource_registry.checks)
        cls.orig_all_registered_checks = deepcopy(BaseCheckRegistry._BaseCheckRegistry__all_registered_checks)
        cls.db_connector = cls.db_connector

    def test_py_graph_check(self):
        if not self.db_connector == RustworkxConnector:
            return
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/py_graph_check_tf_plan"
        valid_dir_path_for_external_check = current_dir + '/py_check_tf_plan'
        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_99999']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=[valid_dir_path_for_external_check],
                            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=checks_allowlist))
        assert len(report.passed_checks) == 3

    def test_runner_two_checks_only(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ["CKV_AWS_21"]
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"], checks=checks_allowlist),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)
        self.assertEqual(report.get_summary()["failed"], 3)
        self.assertEqual(report.get_summary()["passed"], 3)

    def test_tf_plan_filtered_rule(self):
        if not self.db_connector == RustworkxConnector:
            return
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tf_plan_filtered_rule_success.json"
        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_300']
        report = runner.run(files=[valid_plan_path], runner_filter=RunnerFilter(framework=["terraform_plan"], checks=checks_allowlist))
        assert len(report.passed_checks) == 1

    def test_tf_plan_filtered_rule(self):
        if not self.db_connector == RustworkxConnector:
            return
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tf_plan_filtered_rule_fail.json"
        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_300']
        report = runner.run(files=[valid_plan_path], runner_filter=RunnerFilter(framework=["terraform_plan"], checks=checks_allowlist))
        assert len(report.failed_checks) == 1

    def test_runner_record_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()

        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_db_instance"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        checks_allowlist = [custom_check_id]
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=checks_allowlist),
        )

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_runner_check_severity_filter_omit(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()

        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_db_instance"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        checks_allowlist = ['MEDIUM']
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_runner_check_severity_filter_include(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()

        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_db_instance"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]
        checks_allowlist = ['MEDIUM']
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_runner_check_skip_filter_omit(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()

        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_db_instance"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        checks_denylist = ['MEDIUM']
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], skip_checks=checks_denylist),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_runner_check_skip_filter(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()

        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_db_instance"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]
        checks_denylist = ['MEDIUM']
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], skip_checks=checks_denylist),
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_plan_runner_with_empty_vpc_connection(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()
        runner.graph_registry.checks = []

        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"]),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(report.get_summary()["failed"], 106)

    def test_runner_child_modules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_with_child_modules/tfplan.json"
        runner = Runner()
        runner.graph_registry.checks = []
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"]),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(report.get_summary()["failed"], 3)
        self.assertEqual(report.get_summary()["passed"], 4)

    def test_runner_nested_child_modules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_nested_child_modules/tfplan.json"
        runner = Runner()
        runner.graph_registry.checks = []
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=[current_dir + "/extra_yaml_checks"],
            runner_filter=RunnerFilter(framework=["all"]),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(report.get_summary()["failed"], 15)
        self.assertEqual(report.get_summary()["passed"], 3)

        failed_check_ids = set([c.check_id for c in report.failed_checks])
        expected_failed_check_ids = {
            "CKV_AWS_37",
            "CKV_AWS_38",
            "CKV_AWS_39",
            "CKV_AWS_58",
            "CUSTOM_GRAPH_AWS_1"
        }

        assert failed_check_ids == expected_failed_check_ids

        # reset graph checks
        runner.graph_registry.checks = []
        runner.graph_registry.load_checks()

    def test_runner_root_module_resources_no_values(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_root_module_resources_no_values/tfplan.json"
        runner = Runner()
        runner.graph_registry.checks = []
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"]),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        # 4 checks fail on test data for single eks resource as of present
        # If more eks checks are added then this number will need to increase correspondingly to reflect
        # This reasoning holds for all current pass/fails in these tests
        self.assertEqual(report.get_summary()["failed"], 4)
        self.assertEqual(report.get_summary()["passed"], 1)

        failed_check_ids = set([c.check_id for c in report.failed_checks])
        expected_failed_check_ids = {
            "CKV_AWS_37",
            "CKV_AWS_38",
            "CKV_AWS_39",
            "CKV_AWS_58",
        }

        assert failed_check_ids == expected_failed_check_ids

        # reset graph checks
        runner.graph_registry.checks = []
        runner.graph_registry.load_checks()

    def test_runner_root_module_resources_no_values_route53(self):
        #given
        plan_file = Path(__file__).parent / "resources/plan_root_module_resources_no_values/tfplan_route53.json"

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(plan_file)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_38", "CKV2_AWS_39"]),
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["passed"], 1)

        passed_check_ids = set(c.check_id for c in report.passed_checks)
        expected_passed_check_ids = {"CKV2_AWS_39"}

        self.assertCountEqual(passed_check_ids, expected_passed_check_ids)

    def test_runner_data_resource_partial_values(self):
        # In rare circumstances a data resource with partial values in the plan could cause false negatives
        # Often 'data' does not even appear in the *_modules[x].resouces field within planned_values and is not scanned as expected
        # It can occur when tf module B depends on tf module A
        # And tf module A creates a resource that is used in a data block in tf module B
        # So some values can be known but other are not at plan time
        # This can cause the data block resource to be scanned as if it were a managed resource which is not configured correctly
        # See 'Modes': https://www.terraform.io/docs/internals/json-format.html#values-representation
        # This test verifies that such a circumstance stops occurring
        # There is a EKS Managed Resource and a EKS Data Resource
        # The EKS Managed Resource should have 4 failures corresponding with EKS checks.
        # The EKS Data Resource should not be scanned. Previously this would cause 8 failures.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_data_resource_partial_values/tfplan.json"
        runner = Runner()
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"]),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(report.get_summary()["failed"], 4)
        self.assertEqual(report.get_summary()["passed"], 1)

        failed_check_ids = set([c.check_id for c in report.failed_checks])
        expected_failed_check_ids = {
            "CKV_AWS_37",
            "CKV_AWS_38",
            "CKV_AWS_39",
            "CKV_AWS_58",
        }

        assert failed_check_ids == expected_failed_check_ids

    def test_runner_root_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = current_dir + "/resources"
        runner = Runner()
        report = runner.run(
            root_folder=root_dir, files=None, external_checks_dir=None, runner_filter=RunnerFilter(framework=["all"])
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertGreaterEqual(report.get_summary()["failed"], 71)
        self.assertGreaterEqual(report.get_summary()["passed"], 65)

        files_scanned = list(set(map(lambda rec: rec.file_path, report.failed_checks)))
        self.assertGreaterEqual(len(files_scanned), 6)

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = current_dir + "/resources"
        runner = Runner()
        filter = RunnerFilter(framework=['terraform_plan'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.TERRAFORM_PLAN: Severities[BcSeverities.OFF]}
        report = runner.run(
            root_folder=root_dir, files=None, external_checks_dir=None, runner_filter=filter
        )
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)

    def test_record_relative_path_with_relative_dir(self):
        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources", "plan")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ["CKV_AWS_6"]
        report = runner.run(
            root_folder=dir_rel_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        for record in all_checks:
            self.assertEqual(record.repo_file_path, f'/{os.path.join(dir_rel_path, record.file_path.lstrip("/"))}')

    def test_record_relative_path_with_relative_file(self):
        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "plan", "tfplan.json")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=None,
            external_checks_dir=None,
            files=[file_rel_path],
            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        for record in all_checks:
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_runner_unexpected_eks_node_group_remote_access(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/unexpected/eks_node_group_remote_access.json"
        runner = Runner()
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"]),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(report.get_summary()["failed"], 0)
        self.assertEqual(report.get_summary()["passed"], 1)

    def test_runner_with_resource_reference(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_with_resource_reference/tfplan.json"
        allowed_checks = ["CKV_AWS_84"]

        report = Runner().run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["all"], checks=allowed_checks),
        )

        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(report.get_summary()["failed"], 0)
        self.assertEqual(report.get_summary()["passed"], 1)

    def test_runner_with_resource_reference_graph_check(self):
        # given
        valid_plan_path = Path(__file__).parent / "resources/plan_with_resource_reference/tfplan_graph.json"
        allowed_checks = ["CKV2_AWS_6"]

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(valid_plan_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=allowed_checks),
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["passed"], 1)

    def test_runner_with_resource_reference_extra_ref(self):
        # given
        valid_plan_path = Path(__file__).parent / "resources/plan_with_resource_reference/tfplan_extra_ref.json"
        extra_checks_dir_path = [str(Path(__file__).parent / "extra_tf_plan_checks")]
        allowed_checks = ["CUSTOM_CONNECTION_1"]

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(valid_plan_path)],
            external_checks_dir=extra_checks_dir_path,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=allowed_checks),
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 4)

    def test_runner_skip_graph_when_no_plan_exists(self):
        # given
        tf_file_path = Path(__file__).parent / "resource/example/example.tf"

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"]),
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 0)

    def test_runner_utf_16_encoded(self):
        # given
        tf_file_path = Path(__file__).parent / "resources/plan_with_utf_16_encoding/tfplan.json"

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"]),
        )

        # then
        summary = report.get_summary()

        self.assertGreater(summary["failed"], 0)
        self.assertGreater(summary["passed"], 0)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

    def test_runner_line_numbers(self):
        # given
        tf_file_path = Path(__file__).parent / "resources/plan_with_resource_reference/tfplan.json"

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"]),
        )

        # then
        failed_check = report.failed_checks[0]
        self.assertEqual(failed_check.file_line_range, [13, 19])

    def test_runner_ignore_lifecycle_checks(self):
        # given
        tf_file_path = Path(__file__).parent / "resources/plan_with_lifecycle_check/tfplan.json"

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"]),
        )

        # then
        self.assertEqual(len(report.failed_checks), 0)

    def test_runner_extra_check(self):
        # given
        current_dir = Path(__file__).parent
        tf_dir_path = str(current_dir / "resources/plan_with_deleted_resources")
        extra_checks_dir_path = [str(current_dir / "extra_tf_plan_checks")]

        # when
        report = Runner().run(
            root_folder=tf_dir_path,
            external_checks_dir=extra_checks_dir_path,
            runner_filter=RunnerFilter(checks=["CUSTOM_DELETE_1", "CUSTOM_DELETE_2"])
        )

        # then
        summary = report.get_summary()
        self.assertEqual(summary["failed"], 2)

        resource_ids = [check.resource for check in report.failed_checks]
        self.assertCountEqual(resource_ids,["aws_secretsmanager_secret.default", "aws_secretsmanager_secret.default"])

        # check also the details
        failed_check = next(check for check in report.failed_checks if check.check_id == "CUSTOM_DELETE_1")
        self.assertEqual(failed_check.details, ["some great details"])

    def test_runner_nested_child_modules_with_connections(self):
        # given
        tf_file_path = Path(__file__).parent / "resources/plan_nested_child_modules_with_connections/tfplan.json"

        passing_resources = {
            "module.s3_module.module.s3_submodule.aws_s3_bucket.submodule_bucket",
            "module.s3_module.aws_s3_bucket.module_bucket",
            "aws_s3_bucket.root_bucket",
        }
        failing_resources = {
            "module.s3_bucket.aws_s3_bucket.this[0]",
        }

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_6"]),
        )

        # then
        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(len(report.failed_checks), 1)

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_runner_with_iam_policies(self):
        # given
        tf_file_path = Path(__file__).parent / "resources/plan_with_iam_policies/tfplan.json"

        passing_resources = {
            "aws_iam_policy.policy_pass",
        }
        failing_resources = {
            "aws_iam_role_policy.fail_1",
            "aws_iam_group_policy.fail_2",
            "aws_iam_user_policy.fail_3",
        }

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_40", "CKV_AWS_287"]),
        )

        # then
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 2)  # "aws_iam_policy.policy_pass" passes both checks
        self.assertEqual(summary["failed"], 6)  # the rest fails both checks

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_runner_with_iam_data_block(self):
        # given
        tf_file_path = Path(__file__).parent / "resources/plan_with_iam_data_block/tfplan.json"

        failing_resources = {
            "data.aws_iam_policy_document.allow_access_from_another_account",
        }

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV_AWS_49"]),
        )

        # then
        summary = report.get_summary()
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 1)

        failed_check_resources = {c.resource for c in report.failed_checks}
        self.assertEqual(failing_resources, failed_check_resources)

    @mock.patch.dict(os.environ, {'CHECKOV_EXPERIMENTAL_CROSS_VARIABLE_EDGES': 'True'})
    def test_plan_and_tf_combine_graph(self):
        tf_file_path = Path(__file__).parent / "resources/plan_and_tf_combine_graph/tfplan.json"

        repo_path = Path(__file__).parent / "resources/plan_and_tf_combine_graph"

        # deep_analysis disabled
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_6"], deep_analysis=False,
                                       repo_root_for_plan_enrichment=[repo_path])
        )

        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 2)

        # deep_analysis enabled
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_6"], deep_analysis=True, repo_root_for_plan_enrichment=[repo_path])
        )

        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(len(report.failed_checks), 0)

        expected_addresses = ['aws_s3_bucket.example', 'aws_s3_bucket.example_2']
        report_addresses = [report.passed_checks[0].resource_address, report.passed_checks[1].resource_address]
        assert sorted(expected_addresses) == sorted(report_addresses)
        assert report.passed_checks[0].file_path.endswith('.json')
        assert report.passed_checks[1].file_path.endswith('.json')

    def test_plan_and_tf_combine_graph_with_missing_resources(self):
        tf_file_path = Path(__file__).parent / "resources/plan_and_tf_combine_graph_with_missing_resources/tfplan.json"
        repo_path = Path(__file__).parent / "resources/plan_and_tf_combine_graph_with_missing_resources"

        # deep_analysis disabled
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_61"], deep_analysis=False,
                                       repo_root_for_plan_enrichment=[repo_path])
        )

        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 2)

        # deep_analysis enabled
        report = Runner().run(
            root_folder=None,
            files=[str(tf_file_path)],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CKV2_AWS_61"], deep_analysis=True,
                                       repo_root_for_plan_enrichment=[repo_path])
        )

        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 2)

        expected_addresses = ['aws_s3_bucket.example', 'aws_s3_bucket.example_2']
        report_addresses = [report.failed_checks[0].resource_address, report.failed_checks[1].resource_address]
        assert sorted(expected_addresses) == sorted(report_addresses)

    def test_plan_resources_ids(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_resources_ids_with_nested_modules/tfplan.json"
        valid_resources_ids = ["module.child_0.module.child_1_c.aws_eks_cluster.cluster",
                               "module.child_0.module.child_1_b.aws_eks_cluster.cluster",
                               "module.child_0.module.child_1_a.aws_eks_cluster.cluster"]
        runner = Runner()
        runner.graph_registry.checks = []
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=[current_dir + "/extra_yaml_checks"],
            runner_filter=RunnerFilter(framework=["terraform_plan"]),
        )
        self.assertGreater(report.get_summary()["failed"] + report.get_summary()["passed"], 0)

        for check in itertools.chain(report.failed_checks, report.passed_checks):
            self.assertIn(check.resource, valid_resources_ids)

        self.assertEqual(len(report.resources), 3)

    def test_plan_resources_created_by_modules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/extra_tf_plan_checks/modules.json"
        runner = Runner()
        report = runner.run(
            root_folder=None, external_checks_dir=None, files=[valid_plan_path],
            runner_filter=RunnerFilter(checks=['CKV2_GCP_12', 'CKV_GCP_88'])
        )
        passed_checks_CKV2_GCP_12 = [check for check in report.passed_checks if check.check_id == 'CKV2_GCP_12']
        passed_checks_CKV_GCP_88 = [check for check in report.passed_checks if check.check_id == 'CKV_GCP_88']

        assert passed_checks_CKV2_GCP_12[0].resource == 'module.achia_test_valid_443.google_compute_firewall.custom[0]'
        assert passed_checks_CKV2_GCP_12[1].resource == 'module.achia_test_valid_ports.google_compute_firewall.custom[0]'
        assert passed_checks_CKV2_GCP_12[2].resource == 'module.achia_test_violating_no_ports.google_compute_firewall.custom[0]'
        assert passed_checks_CKV2_GCP_12[3].resource == 'module.achia_test_violating_port.google_compute_firewall.custom[0]'

        assert passed_checks_CKV_GCP_88[0].resource == 'module.achia_test_valid_443.google_compute_firewall.custom[0]'
        assert passed_checks_CKV_GCP_88[1].resource == 'module.achia_test_valid_ports.google_compute_firewall.custom[0]'
        assert passed_checks_CKV_GCP_88[2].resource == 'module.achia_test_violating_no_ports.google_compute_firewall.custom[0]'
        assert passed_checks_CKV_GCP_88[3].resource == 'module.achia_test_violating_port.google_compute_firewall.custom[0]'

    def test___get_file_path__with_tf_definition_key_uses_correct_file_path(self):
        tf_definition = TFDefinitionKey(file_path='test')
        file_path, scanned_file = Runner()._get_file_path(tf_definition, 'test')
        assert file_path == 'test'
        assert scanned_file == '/.'

    def test_plan_change_keys(self):
        # given
        current_dir = Path(__file__).parent
        tf_plan_path = current_dir / "resources/plan_change_keys/tfplan.json"
        external_checks_dir = current_dir / "extra_tf_plan_checks"

        # when
        report = Runner().run(
            root_folder=None,
            files=[str(tf_plan_path)],
            external_checks_dir=[str(external_checks_dir)],
            runner_filter=RunnerFilter(framework=["terraform_plan"], checks=["CUSTOM_CHANGE_1"]),
        )

        # then
        summary = report.get_summary()

        passing_resources = {
            'aws_security_group_rule.foo'
        }
        failing_resources = {
            'aws_security_group_rule.bar',
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 2)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def tearDown(self) -> None:
        resource_registry.checks = deepcopy(self.orig_checks)
        BaseCheckRegistry._BaseCheckRegistry__all_registered_checks = deepcopy(self.orig_all_registered_checks)


if __name__ == "__main__":
    unittest.main()
