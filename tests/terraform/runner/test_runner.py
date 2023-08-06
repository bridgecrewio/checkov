import inspect
import os
import shutil
import unittest
import dis
from collections import defaultdict
from pathlib import Path

# do not remove; prevents circular import error
from typing import Dict, Any
from unittest import mock
from igraph import Graph
from networkx import DiGraph
from parameterized import parameterized, parameterized_class

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.output.report import Report
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.parser_utils import TERRAFORM_NESTED_MODULE_PATH_PREFIX, TERRAFORM_NESTED_MODULE_PATH_ENDING, \
    TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR
from checkov.runner_filter import RunnerFilter
from checkov.terraform import TFDefinitionKey
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.parser import Parser
from checkov.terraform.runner import Runner
from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.checks.provider.registry import provider_registry
from checkov.terraform.checks.data.registry import data_registry

CUSTOM_GRAPH_CHECK_ID = 'CKV2_CUSTOM_1'
EXTERNAL_MODULES_DOWNLOAD_PATH = os.environ.get('EXTERNAL_MODULES_DIR', DEFAULT_EXTERNAL_MODULES_DIR)


@parameterized_class([
    {"db_connector": NetworkxConnector, "use_new_tf_parser": "True", "tf_split_graph": "True", "graph": "NETWORKX"},
    {"db_connector": NetworkxConnector, "use_new_tf_parser": "True", "tf_split_graph": "False", "graph": "NETWORKX"},
    {"db_connector": NetworkxConnector, "use_new_tf_parser": "False", "tf_split_graph": "False", "graph": "NETWORKX"},
    {"db_connector": IgraphConnector, "use_new_tf_parser": "True", "tf_split_graph": "True", "graph": "IGRAPH"},
    {"db_connector": IgraphConnector, "use_new_tf_parser": "True", "tf_split_graph": "False", "graph": "IGRAPH"},
    {"db_connector": IgraphConnector, "use_new_tf_parser": "False", "tf_split_graph": "False", "graph": "IGRAPH"}
])
class TestRunnerValid(unittest.TestCase):
    def setUp(self) -> None:
        self.orig_checks = resource_registry.checks
        self.db_connector = self.db_connector
        os.environ["CHECKOV_GRAPH_FRAMEWORK"] = self.graph
        os.environ["CHECKOV_NEW_TF_PARSER"] = self.use_new_tf_parser
        os.environ["TF_SPLIT_GRAPH"] = self.tf_split_graph

    def tearDown(self):
        del os.environ["CHECKOV_GRAPH_FRAMEWORK"]
        del os.environ["CHECKOV_NEW_TF_PARSER"]
        del os.environ["TF_SPLIT_GRAPH"]

    def test_registry_has_type(self):
        self.assertEqual(resource_registry.report_type, CheckType.TERRAFORM)
        self.assertEqual(provider_registry.report_type, CheckType.TERRAFORM)
        self.assertEqual(module_registry.report_type, CheckType.TERRAFORM)
        self.assertEqual(data_registry.report_type, CheckType.TERRAFORM)

    def test_runner_two_checks_only(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_41', 'CKV_AZURE_1']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["all"], checks=checks_allowlist))
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)

    def test_runner_denylist_checks(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner(db_connector=self.db_connector())
        checks_denylist = ['CKV_AWS_41', 'CKV_AZURE_1']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["all"], skip_checks=checks_denylist))
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)
        for record in report.failed_checks:
            self.assertNotIn(record.check_id, checks_denylist)

    def test_runner_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertGreaterEqual(summary['failed'], 1)
        self.assertEqual(summary["parsing_errors"], 1)
        report.print_json()
        report.print_console()
        report.print_console(is_quiet=True)
        report.print_console(is_quiet=True, is_compact=True)
        report.print_failed_github_md()

    def test_runner_passing_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_dir_path = current_dir + "/resources/valid_tf_only_passed_checks"

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=passing_tf_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(9, summary['failed'])
        self.assertEqual(1, summary['skipped'])
        self.assertEqual(0, summary["parsing_errors"])

    def test_runner_passing_multi_line_ternary_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/mutli_line_ternary"

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=None)
        self.assertListEqual(report.parsing_errors, [])

    def test_runner_extra_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # should load checks recursively

        tf_dir_path = current_dir + "/resources/extra_check_test"
        extra_checks_dir_path = [current_dir + "/extra_checks"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=extra_checks_dir_path)
        report_json = report.get_json()
        for check in resource_registry.checks["aws_s3_bucket"]:
            if check.id in ("CUSTOM_AWS_1", "CUSTOM_AWS_2"):
                resource_registry.checks["aws_s3_bucket"].remove(check)
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())

        passing_custom = 0
        failed_custom = 0
        for record in report.passed_checks:
            if record.check_id in ("CUSTOM_AWS_1", "CUSTOM_AWS_2"):
                passing_custom = passing_custom + 1
        for record in report.failed_checks:
            if record.check_id in ("CUSTOM_AWS_1", "CUSTOM_AWS_2"):
                failed_custom = failed_custom + 1

        self.assertEqual(2, passing_custom)
        self.assertEqual(4, failed_custom)
        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_runner_extra_yaml_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/extra_check_test"
        extra_checks_dir_path = [current_dir + "/extra_yaml_checks"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=extra_checks_dir_path)
        report_json = report.get_json()
        for check in resource_registry.checks["aws_s3_bucket"]:
            if check.id in ("CUSTOM_AWS_1", "CUSTOM_AWS_2"):
                resource_registry.checks["aws_s3_bucket"].remove(check)
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())

        passing_custom = 0
        failed_custom = 0
        for record in report.passed_checks:
            if record.check_id == "CKV2_CUSTOM_1":
                passing_custom = passing_custom + 1
        for record in report.failed_checks:
            if record.check_id == "CKV2_CUSTOM_1":
                failed_custom = failed_custom + 1

        self.assertEqual(passing_custom, 0)
        self.assertEqual(failed_custom, 3)

        graph_record = next(record for record in report.failed_checks if record.check_id == "CKV2_CUSTOM_1")
        self.assertEqual(graph_record.guideline, "https://docs.bridgecrew.io/docs/ckv2_custom_1")

        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_runner_provider_yaml_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/provider_blocks"
        extra_checks_dir_path = [current_dir + "/extra_yaml_checks"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=extra_checks_dir_path,
                            runner_filter=RunnerFilter(checks=['CUSTOM_GRAPH_AWS_3', 'CUSTOM_GRAPH_AWS_4']))
        report_json = report.get_json()

        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())

        self.assertEqual(7, len(report.passed_checks))
        self.assertEqual(3, len(report.failed_checks))

        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if
                                           "CUSTOM" not in check.id]

    def test_runner_yaml_module_check(self):
        # given
        current_dir = Path(__file__).parent
        tf_dir_path = current_dir / "resources/module_check"
        extra_checks_dir_path = current_dir / "extra_yaml_checks"
        runner = Runner(db_connector=self.db_connector())

        # when
        report = runner.run(
            root_folder=str(tf_dir_path),
            external_checks_dir=[str(extra_checks_dir_path)],
            runner_filter=RunnerFilter(checks=["CUSTOM_GRAPH_AWS_2"])
        )

        # then
        summary = report.get_summary()

        passing_resources = {"pass"}
        failing_resources = {"fail"}

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_runner_specific_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/valid_tf_only_passed_checks/example.tf"

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[passing_tf_file_path])
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        # self.assertEqual(report.get_exit_code(), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(5, summary['failed'])
        self.assertEqual(0, summary["parsing_errors"])

    def test_check_ids_dont_collide(self):
        runner = Runner(db_connector=self.db_connector())
        unique_checks = {}
        bad_checks = []
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                if check.id not in unique_checks:
                    unique_checks[check.id] = check
                elif check != unique_checks[check.id]:
                    # A single check can have multiple resource blocks it checks, which means it will show up multiple times in the registry
                    bad_checks.append(f'{check.id}: {check.name}')
                    print(f'{check.id}: {check.name}')
        self.assertEqual(len(bad_checks), 0, f'Bad checks: {bad_checks}')

    def test_no_missing_ids(self):
        runner = Runner(db_connector=self.db_connector())
        unique_checks = set()
        graph_checks = []

        # python checks
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                unique_checks.add(check.id)

        # graph checks
        graph_registry = get_graph_checks_registry("terraform")
        graph_registry.load_checks()
        for check in graph_registry.checks:
            if check.id.startswith("CKV_"):
                unique_checks.add(check.id)
            else:
                graph_checks.append(check)

        aws_checks = sorted(
            list(filter(lambda check_id: check_id.startswith("CKV_AWS_"), unique_checks)),
            reverse=True,
            key=lambda s: int(s.split('_')[-1])
        )
        for i in range(1, len(aws_checks) + 8):
            if f'CKV_AWS_{i}' == 'CKV_AWS_4':
                # CKV_AWS_4 was deleted due to https://github.com/bridgecrewio/checkov/issues/371
                continue
            if f'CKV_AWS_{i}' in ('CKV_AWS_132', 'CKV_AWS_125', 'CKV_AWS_151', 'CKV_AWS_128'):
                # These checks were removed because they were duplicates
                continue
            if f'CKV_AWS_{i}' in 'CKV_AWS_95':
                # CKV_AWS_95 is currently implemented just on cfn - actually is CKV_AWS_76
                continue
            if f'CKV_AWS_{i}' == 'CKV_AWS_52':
                # CKV_AWS_52 was deleted since it cannot be toggled in terraform.
                continue
            if f'CKV_AWS_{i}' == 'CKV_AWS_299':
                # CKV_AWS_299 was deleted because AWS doesn't support it and seems to be a bug in Terraform.
                # https://github.com/hashicorp/terraform-provider-aws/issues/31821
                continue
            self.assertIn(f'CKV_AWS_{i}', aws_checks, msg=f'The new AWS violation should have the ID "CKV_AWS_{i}"')

        gcp_checks = sorted(
            list(filter(lambda check_id: '_GCP_' in check_id, unique_checks)),
            reverse=True,
            key=lambda s: int(s.split('_')[-1])
        )
        for i in range(1, len(gcp_checks) + 2):
            if f'CKV_GCP_{i}' == 'CKV_GCP_5':
                # CKV_GCP_5 is no longer a valid platform check
                continue
            if f'CKV_GCP_{i}' == 'CKV_GCP_67':
                # CKV_GCP_67 is not deployable anymore https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#protect_node_metadata
                continue

            self.assertIn(f'CKV_GCP_{i}', gcp_checks, msg=f'The new GCP violation should have the ID "CKV_GCP_{i}"')

        azure_checks = sorted(
            list(filter(lambda check_id: '_AZURE_' in check_id, unique_checks)),
            reverse=True,
            key=lambda s: int(s.split('_')[-1])
        )
        for i in range(1, len(azure_checks) + 4):
            if f'CKV_AZURE_{i}' == 'CKV_AZURE_46':
                continue  # this rule has been merged into a v2 graph implementation -> CKV_AZURE_24
            if f'CKV_AZURE_{i}' == 'CKV_AZURE_51':
                continue  # https://github.com/bridgecrewio/checkov/pull/983
            if f"CKV_AZURE_{i}" == "CKV_AZURE_60":
                continue  # duplicate of CKV_AZURE_3
            if f"CKV_AZURE_{i}" == "CKV_AZURE_90":
                continue  # duplicate of CKV_AZURE_53

            self.assertIn(f'CKV_AZURE_{i}', azure_checks,
                          msg=f'The new Azure violation should have the ID "CKV_AZURE_{i}"')

        alicloud_checks = sorted(
            list(filter(lambda check_id: '_ALI_' in check_id, unique_checks)),
            reverse=True,
            key=lambda s: int(s.split('_')[-1])
        )
        for i in range(1, len(alicloud_checks) + 1):
            if f"CKV_ALI_{i}" == "CKV_ALI_34":
                continue  # duplicate of CKV_ALI_30
            if f"CKV_ALI_{i}" in ("CKV_ALI_39", "CKV_ALI_40"):
                continue  # can't find a reference for it

            self.assertIn(f"CKV_ALI_{i}", alicloud_checks,
                          msg=f'The new Alibaba Cloud violation should have the ID "CKV_ALI_{i}"')

        # add cloudformation checks to graph checks
        graph_registry = get_graph_checks_registry("cloudformation")
        graph_registry.load_checks()
        graph_checks.extend(list(filter(lambda check: 'CKV2_' in check.id, graph_registry.checks)))

        aws_checks, gcp_checks, azure_checks = [], [], []
        for check in graph_checks:
            if '_AWS_' in check.id:
                aws_checks.append(check.id)
            elif '_GCP_' in check.id:
                gcp_checks.append(check.id)
            elif '_AZURE_' in check.id:
                azure_checks.append(check.id)

        for check_list in [aws_checks, gcp_checks, azure_checks]:
            check_list.sort(reverse=True, key=lambda s: int(s.split('_')[-1]))

        for i in range(1, len(aws_checks) + 5):
            if f'CKV2_AWS_{i}' == 'CKV2_AWS_17':
                # CKV2_AWS_17 was overly keen and those resources it checks are created by default
                continue
            if f'CKV2_AWS_{i}' == 'CKV2_AWS_13':
                # CKV2_AWS_13 is not supported by AWS
                continue
            if f'CKV2_AWS_{i}' == 'CKV2_AWS_24':
                # Was a test policy
                continue
            if f'CKV2_AWS_{i}' == 'CKV2_AWS_25':
                # Was a test policy
                continue
            if f'CKV2_AWS_{i}' == 'CKV2_AWS_26':
                # Was a test policy
                continue
            self.assertIn(f'CKV2_AWS_{i}', aws_checks,
                          msg=f'The new AWS violation should have the ID "CKV2_AWS_{i}"')
        for i in range(1, len(gcp_checks) + 1):
            self.assertIn(f'CKV2_GCP_{i}', gcp_checks,
                          msg=f'The new GCP violation should have the ID "CKV2_GCP_{i}"')
        for i in range(1, len(azure_checks) + 2):
            if f'CKV2_AZURE_{i}' == 'CKV2_AZURE_18':
                # duplicate of CKV2_AZURE_1
                continue
            self.assertIn(f'CKV2_AZURE_{i}', azure_checks,
                          msg=f'The new Azure violation should have the ID "CKV2_AZURE_{i}"')

    def test_provider_uniqueness(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/many_providers"
        runner = Runner(db_connector=self.db_connector())
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks='CKV_AWS_41'))
        self.assertEqual(len(result.passed_checks), 17)
        self.assertIn('aws.default', map(lambda record: record.resource, result.passed_checks))

        # check if a one line provider is correctly processed
        provider = next(check for check in result.passed_checks if check.resource == "aws.one-line")
        self.assertIsNotNone(provider.file_line_range)

    def test_entire_resources_folder(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/"
        runner = Runner(db_connector=self.db_connector())
        if isinstance(runner.db_connector, IgraphConnector):
            result = runner.run(root_folder=valid_dir_path, external_checks_dir=None, runner_filter=RunnerFilter(
                checks=['CKV_AWS_21', 'CKV_AWS_42', 'CKV_AWS_62', 'CKV_AWS_53', 'CKV_AWS_18', 'CKV_AWS_61', 'CKV_AWS_144',
                        'CKV_AWS_145', 'CKV_AWS_115', 'CKV_AWS_116', 'CKV_AWS_117', 'CKV_AWS_6', 'CKV_AWS_168', 'CKV_AWS_170',
                        'CKV_AWS_171', 'CKV_AWS_172', 'CKV_AWS_37', 'CKV_AWS_38', 'CKV_AWS_39', 'CKV_AWS_107', 'CKV_AWS_109',
                        'CKV_AWS_110'], framework=['terraform']))
            self.assertEqual(len(result.passed_checks), 52)
            self.assertEqual(len(result.failed_checks), 255)
            self.assertEqual(len(result.skipped_checks), 0)

    def test_modules_folder_with_files_args(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner(db_connector=self.db_connector())
        if isinstance(runner.db_connector, IgraphConnector):
            res = []
            for (dir_path, dir_names, file_names) in os.walk(valid_dir_path):
                for file in file_names:
                    res.append(os.path.join(dir_path, file))
            result = runner.run(files=res, root_folder=None, external_checks_dir=None,
                                runner_filter=RunnerFilter(
                                    checks=['CKV_AWS_21', 'CKV_AWS_42', 'CKV_AWS_62', 'CKV_AWS_109', 'CKV_AWS_168',
                                            'CKV_AWS_53', 'CKV_AWS_18', 'CKV_AWS_61', 'CKV_AWS_144', 'CKV_AWS_170',
                                            'CKV_AWS_145', 'CKV_AWS_115', 'CKV_AWS_116', 'CKV_AWS_117', 'CKV_AWS_6',
                                            'CKV_AWS_171', 'CKV_AWS_172', 'CKV_AWS_37', 'CKV_AWS_38', 'CKV_AWS_39',
                                            'CKV_AWS_107', 'CKV_AWS_110'],
                                    framework=['terraform']))
            self.assertEqual(len(result.passed_checks), 51)
            self.assertEqual(len(result.failed_checks), 263)
            self.assertEqual(len(result.skipped_checks), 0)

    def test_terraform_module_checks_are_performed(self):
        check_name = "TF_M_1"

        from checkov.common.models.enums import CheckResult
        from checkov.terraform.checks.module.base_module_check import BaseModuleCheck
        from checkov.terraform.checks.module.registry import module_registry

        class ModuleCheck(BaseModuleCheck):

            def __init__(self):
                name = "Test check"
                id = check_name
                supported_resources = ['module']
                categories = []
                super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

            def scan_module_conf(self, conf):
                return CheckResult.PASSED

        check = ModuleCheck()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources/valid_tf_only_module_usage")
        runner = Runner(db_connector=self.db_connector())
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks=check_name))

        # unregister check
        for resource in check.supported_resources:
            module_registry.checks[resource].remove(check)

        self.assertEqual(len(result.passed_checks), 1)
        self.assertIn('some-module', map(lambda record: record.resource, result.passed_checks))

    def test_terraform_module_checks_are_performed_even_if_supported_resources_is_omitted(self):
        check_name = "TF_M_2"

        from checkov.common.models.enums import CheckResult
        from checkov.terraform.checks.module.base_module_check import BaseModuleCheck
        from checkov.terraform.checks.module.registry import module_registry

        class ModuleCheck(BaseModuleCheck):

            def __init__(self):
                name = "Test check"
                id = check_name
                categories = []
                super().__init__(name=name, id=id, categories=categories)

            def scan_module_conf(self, conf):
                return CheckResult.PASSED

        check = ModuleCheck()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources/valid_tf_only_module_usage")
        runner = Runner(db_connector=self.db_connector())
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks=check_name))

        # unregister check
        for resource in check.supported_resources:
            module_registry.checks[resource].remove(check)

        self.assertEqual(len(result.passed_checks), 1)
        self.assertIn('some-module', map(lambda record: record.resource, result.passed_checks))

    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    @mock.patch.dict(os.environ, {"TF_SPLIT_GRAPH": "False"})
    @mock.patch.dict(os.environ, {"CHECKOV_ENABLE_FOREACH_HANDLING": "False"})
    def test_terraform_multiple_module_versions(self):
        # given
        root_dir = Path(__file__).parent / "resources/multiple_module_versions"

        # when
        result = Runner(db_connector=self.db_connector()).run(
            root_folder=str(root_dir),
            runner_filter=RunnerFilter(
                checks=["CKV_AWS_88"],
                framework="terraform",
                download_external_modules=True
            )
        )

        # then
        summary = result.get_summary()
        passed_resources = [check.resource for check in result.passed_checks]
        failed_resources = [check.resource for check in result.failed_checks]

        self.assertEqual(4, summary["passed"])
        self.assertEqual(4, summary["failed"])
        self.assertEqual(0, summary['skipped'])
        self.assertEqual(0, summary['parsing_errors'])

        expected_passed_resources = [
            "module.ec2_private_latest.aws_instance.this",
            "module.ec2_private_latest_2.aws_instance.this",
            "module.ec2_private_old.aws_instance.this",
            "module.ec2_private_old_2.aws_instance.this",
        ]
        expected_failed_resources = [
            "module.ec2_public_latest.aws_instance.this",
            "module.ec2_public_latest_2.aws_instance.this",
            "module.ec2_public_old.aws_instance.this",
            "module.ec2_public_old_2.aws_instance.this",
        ]
        self.assertCountEqual(expected_passed_resources, passed_resources)
        self.assertCountEqual(expected_failed_resources, failed_resources)

        # cleanup
        if (root_dir / EXTERNAL_MODULES_DOWNLOAD_PATH).exists():
            shutil.rmtree(root_dir / EXTERNAL_MODULES_DOWNLOAD_PATH)

    def test_parser_error_handled_for_directory_target(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        invalid_dir_path = os.path.join(current_dir, "resources/invalid_terraform_syntax")
        file_names = ['bad_tf_1.tf', 'bad_tf_2.tf']
        invalid_dir_abs_path = os.path.abspath(invalid_dir_path)

        runner = Runner(db_connector=self.db_connector())
        result = runner.run(root_folder=invalid_dir_path, external_checks_dir=None)

        self.assertEqual(len(result.parsing_errors), 2)
        for file in file_names:
            self.assertIn(os.path.join(invalid_dir_abs_path, file), result.parsing_errors)

    def test_parser_error_handled_for_file_target(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        invalid_dir_path = os.path.join(current_dir, "resources/invalid_terraform_syntax")
        file_names = ['bad_tf_1.tf', 'bad_tf_2.tf']
        invalid_dir_abs_path = os.path.abspath(invalid_dir_path)

        runner = Runner(db_connector=self.db_connector())
        result = runner.run(files=[os.path.join(invalid_dir_path, file) for file in file_names], root_folder=None,
                            external_checks_dir=None)

        self.assertEqual(len(result.parsing_errors), 2)
        for file in file_names:
            self.assertIn(os.path.join(invalid_dir_abs_path, file), result.parsing_errors)

    def test_typed_terraform_resource_checks_are_performed(self):
        test_self = self
        check_name = "TF_M_2"
        test_dir = "resources/valid_tf_only_resource_usage"

        from checkov.common.models.enums import CheckResult
        from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
        from checkov.terraform.checks.resource.registry import resource_registry

        class ResourceCheck(BaseResourceCheck):

            def __init__(self):
                name = "Test check"
                id = check_name
                supported_resources = ['*']
                categories = []
                super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

            def scan_entity_conf(self, conf, entity_type):
                if entity_type == 'type_1':
                    test_self.assertIn('a', conf)
                    test_self.assertEqual([1], conf['a'])
                elif entity_type == 'type_2':
                    test_self.assertIn('b', conf)
                    test_self.assertEqual([2], conf['b'])
                else:
                    test_self.fail(f'Unexpected entity_type: {entity_type}. Expected type_1 or type_2, because no '
                                   f'other resources are defined in the files inside of {test_dir}.')
                return CheckResult.PASSED

            def scan_resource_conf(self, conf):
                pass

        check = ResourceCheck()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, test_dir)
        runner = Runner(db_connector=self.db_connector())
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks=check_name))

        # unregister check
        for resource in check.supported_resources:
            resource_registry.wildcard_checks[resource].remove(check)

        self.assertEqual(len(result.passed_checks), 2)

    def test_external_definitions_context(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/valid_tf_only_passed_checks"
        external_definitions_context = {
            f"{current_dir}/resources/valid_tf_only_passed_checks/example.tf": {
                "resource": {
                    "aws_s3_bucket": {
                        "foo-bucket": {
                            "start_line": 1,
                            "end_line": 34,
                            "code_lines": [
                                (1, 'resource "aws_s3_bucket" "foo-bucket" {\n'),
                                (2, "  region        = var.region\n"),
                                (3, "  bucket        = local.bucket_name\n"),
                                (4, "  force_destroy = true\n"),
                                (5, "  tags = {\n"),
                                (6, '    Name = "foo-${data.aws_caller_identity.current.account_id}"\n'),
                                (7, "  }\n"),
                                (8, "  versioning {\n"),
                                (9, "    enabled = true\n"),
                                (10, "    mfa_delete = true\n"),
                                (11, "  }\n"),
                                (12, "  logging {\n"),
                                (13, '    target_bucket = "${aws_s3_bucket.log_bucket.id}"\n'),
                                (14, '    target_prefix = "log/"\n'),
                                (15, "  }\n"),
                                (16, "  server_side_encryption_configuration {\n"),
                                (17, "    rule {\n"),
                                (18, "      apply_server_side_encryption_by_default {\n"),
                                (19, '        kms_master_key_id = "${aws_kms_key.mykey.arn}"\n'),
                                (20, '        sse_algorithm     = "aws:kms"\n'),
                                (21, "      }\n"),
                                (22, "    }\n"),
                                (23, "  }\n"),
                                (24, '  acl           = "private"\n'),
                                (25, '  tags = "${merge\n'),
                                (26, "    (\n"),
                                (27, "      var.common_tags,\n"),
                                (28, "      map(\n"),
                                (29, '        "name", "VM Virtual Machine",\n'),
                                (30, '        "group", "foo"\n'),
                                (31, "      )\n"),
                                (32, "    )\n"),
                                (33, '  }"\n'),
                                (34, "}\n"),
                            ],
                            "skipped_checks": [],
                        }
                    },
                    "null_resource": {
                        "example": {
                            "start_line": 36,
                            "end_line": 46,
                            "code_lines": [
                                (36, 'resource "null_resource" "example" {\n'),
                                (37, '  tags = "${merge\n'),
                                (38, "(\n"),
                                (39, "var.common_tags,\n"),
                                (40, "map(\n"),
                                (41, '"name", "VM Base Post Provisioning Library",\n'),
                                (42, '"group", "aut",\n'),
                                (43, '"dependency", "${var.input_dependency_value}")\n'),
                                (44, ")\n"),
                                (45, '}"\n'),
                                (46, "}\n"),
                            ],
                            "skipped_checks": [],
                        }
                    },
                },
                "data": {
                    "aws_caller_identity": {
                        "current": {"start_line": 47, "end_line": 0, "code_lines": [], "skipped_checks": []}
                    }
                },
                "provider": {
                    "kubernetes": {
                        "default": {
                            "start_line": 49,
                            "end_line": 55,
                            "code_lines": [
                                (49, 'provider "kubernetes" {\n'),
                                (50, '  version                = "1.10.0"\n'),
                                (51, "  host                   = module.aks_cluster.kube_config.0.host\n"),
                                (
                                    52,
                                    "  client_certificate     = base64decode(module.aks_cluster.kube_config.0.client_certificate)\n",
                                ),
                                (
                                    53,
                                    "client_key             = base64decode(module.aks_cluster.kube_config.0.client_key)\n",
                                ),
                                (
                                    54,
                                    "cluster_ca_certificate = base64decode(module.aks_cluster.kube_config.0.cluster_ca_certificate)\n",
                                ),
                                (55, "}\n"),
                            ],
                            "skipped_checks": [],
                        }
                    }
                },
                "module": {
                    "new_relic": {
                        "start_line": 57,
                        "end_line": 67,
                        "code_lines": [
                            (57, 'module "new_relic" {\n'),
                            (
                                58,
                                'source                            = "s3::https://s3.amazonaws.com/my-artifacts/new-relic-k8s-0.2.5.zip"\n',
                            ),
                            (59, "kubernetes_host                   = module.aks_cluster.kube_config.0.host\n"),
                            (
                                60,
                                "kubernetes_client_certificate     = base64decode(module.aks_cluster.kube_config.0.client_certificate)\n",
                            ),
                            (
                                61,
                                "kubernetes_client_key             = base64decode(module.aks_cluster.kube_config.0.client_key)\n",
                            ),
                            (
                                62,
                                "kubernetes_cluster_ca_certificate = base64decode(module.aks_cluster.kube_config.0.cluster_ca_certificate)\n",
                            ),
                            (63, "cluster_name                      = module.naming_conventions.aks_name\n"),
                            (
                                64,
                                'new_relic_license                 = data.vault_generic_secret.new_relic_license.data["license"]\n',
                            ),
                            (
                                65,
                                "cluster_ca_bundle_b64             = module.aks_cluster.kube_config.0.cluster_ca_certificate\n",
                            ),
                            (66, "module_depends_on                 = [null_resource.delay_aks_deployments]\n"),
                            (67, "}"),
                        ],
                        "skipped_checks": [],
                    }
                },
            },
            f"{current_dir}/resources/valid_tf_only_passed_checks/example_skip_acl.tf": {
                "resource": {
                    "aws_s3_bucket": {
                        "foo-bucket": {
                            "start_line": 1,
                            "end_line": 26,
                            "code_lines": [
                                (1, 'resource "aws_s3_bucket" "foo-bucket" {\n'),
                                (2, "  region        = var.region\n"),
                                (3, "  bucket        = local.bucket_name\n"),
                                (4, "  force_destroy = true\n"),
                                (5, "  #checkov:skip=CKV_AWS_20:The bucket is a public static content host\n"),
                                (6, "  #bridgecrew:skip=CKV_AWS_52: foo\n"),
                                (7, "  tags = {\n"),
                                (8, '    Name = "foo-${data.aws_caller_identity.current.account_id}"\n'),
                                (9, "  }\n"),
                                (10, "  versioning {\n"),
                                (11, "    enabled = true\n"),
                                (12, "  }\n"),
                                (13, "  logging {\n"),
                                (14, '    target_bucket = "${aws_s3_bucket.log_bucket.id}"\n'),
                                (15, '    target_prefix = "log/"\n'),
                                (16, "  }\n"),
                                (17, "  server_side_encryption_configuration {\n"),
                                (18, "    rule {\n"),
                                (19, "      apply_server_side_encryption_by_default {\n"),
                                (20, '        kms_master_key_id = "${aws_kms_key.mykey.arn}"\n'),
                                (21, '        sse_algorithm     = "aws:kms"\n'),
                                (22, "      }\n"),
                                (23, "    }\n"),
                                (24, "  }\n"),
                                (25, '  acl           = "public-read"\n'),
                                (26, "}\n"),
                            ],
                            "skipped_checks": [
                                {"id": "CKV_AWS_20", "suppress_comment": "The bucket is a public static content host"},
                                {"id": "CKV_AWS_52", "suppress_comment": " foo"},
                            ],
                        }
                    }
                },
                "data": {
                    "aws_caller_identity": {
                        "current": {"start_line": 27, "end_line": 0, "code_lines": [], "skipped_checks": []}
                    }
                },
            },
        }
        tf_definitions = {
            f"{current_dir}/resources/valid_tf_only_passed_checks/example.tf": {
                "resource": [
                    {
                        "aws_s3_bucket": {
                            "foo-bucket": {
                                "region": ["${var.region}"],
                                "bucket": ["${local.bucket_name}"],
                                "force_destroy": [True],
                                "versioning": [{"enabled": [True], "mfa_delete": [True]}],
                                "logging": [
                                    {"target_bucket": ["${aws_s3_bucket.log_bucket.id}"], "target_prefix": ["log/"]}
                                ],
                                "server_side_encryption_configuration": [
                                    {
                                        "rule": [
                                            {
                                                "apply_server_side_encryption_by_default": [
                                                    {
                                                        "kms_master_key_id": ["${aws_kms_key.mykey.arn}"],
                                                        "sse_algorithm": ["aws:kms"],
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ],
                                "acl": ["private"],
                                "tags": [
                                    '${merge\n    (\n      var.common_tags,\n      map(\n        "name", "VM Virtual Machine",\n        "group", "foo"\n      )\n    )\n  }'
                                ],
                            }
                        }
                    }
                ],
                "data": [{"aws_caller_identity": {"current": {}}}],
                "provider": [
                    {
                        "kubernetes": {
                            "version": ["1.10.0"],
                            "host": ["${module.aks_cluster.kube_config[0].host}"],
                            "client_certificate": [
                                "${base64decode(module.aks_cluster.kube_config[0].client_certificate)}"
                            ],
                            "client_key": ["${base64decode(module.aks_cluster.kube_config[0].client_key)}"],
                            "cluster_ca_certificate": [
                                "${base64decode(module.aks_cluster.kube_config[0].cluster_ca_certificate)}"
                            ],
                        }
                    }
                ],
                "module": [
                    {
                        "new_relic": {
                            "source": ["s3::https://s3.amazonaws.com/my-artifacts/new-relic-k8s-0.2.5.zip"],
                            "kubernetes_host": ["${module.aks_cluster.kube_config[0].host}"],
                            "kubernetes_client_certificate": [
                                "${base64decode(module.aks_cluster.kube_config[0].client_certificate)}"
                            ],
                            "kubernetes_client_key": ["${base64decode(module.aks_cluster.kube_config[0].client_key)}"],
                            "kubernetes_cluster_ca_certificate": [
                                "${base64decode(module.aks_cluster.kube_config[0].cluster_ca_certificate)}"
                            ],
                            "cluster_name": ["${module.naming_conventions.aks_name}"],
                            "new_relic_license": ['${data.vault_generic_secret.new_relic_license.data["license"]}'],
                            "cluster_ca_bundle_b64": ["${module.aks_cluster.kube_config[0].cluster_ca_certificate}"],
                            "module_depends_on": [["${null_resource.delay_aks_deployments}"]],
                        }
                    }
                ],
            },
            f"{current_dir}/resources/valid_tf_only_passed_checks/example_skip_acl.tf": {
                "resource": [
                    {
                        "aws_s3_bucket": {
                            "foo-bucket": {
                                "region": ["${var.region}"],
                                "bucket": ["${local.bucket_name}"],
                                "force_destroy": [True],
                                "tags": [{"Name": "foo-${data.aws_caller_identity.current.account_id}"}],
                                "versioning": [{"enabled": [True]}],
                                "logging": [
                                    {"target_bucket": ["${aws_s3_bucket.log_bucket.id}"], "target_prefix": ["log/"]}
                                ],
                                "server_side_encryption_configuration": [
                                    {
                                        "rule": [
                                            {
                                                "apply_server_side_encryption_by_default": [
                                                    {
                                                        "kms_master_key_id": ["${aws_kms_key.mykey.arn}"],
                                                        "sse_algorithm": ["aws:kms"],
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ],
                                "acl": ["public-read"],
                            }
                        }
                    }
                ],
                "data": [{"aws_caller_identity": {"current": {}}}],
            },
        }
        runner = Runner(db_connector=self.db_connector())
        parser = Parser()
        runner.definitions = tf_definitions
        runner.set_external_data(tf_definitions, external_definitions_context, breadcrumbs={})
        parser.parse_directory(tf_dir_path, tf_definitions)
        report = Report('terraform')
        runner.check_tf_definition(root_folder=tf_dir_path, report=report, runner_filter=RunnerFilter())
        self.assertGreaterEqual(len(report.passed_checks), 1)

    def test_failure_in_resolved_module(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "../parser/resources/parser_scenarios/module_matryoshka_nested_module_enable")
        valid_dir_path = os.path.normpath(valid_dir_path)
        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist))
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suite())
        self.assertEqual(report.get_exit_code({'soft_fail': False, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 1)
        self.assertEqual(report.get_exit_code({'soft_fail': True, 'soft_fail_checks': [], 'soft_fail_threshold': None, 'hard_fail_checks': [], 'hard_fail_threshold': None}), 0)

        self.assertEqual(checks_allowlist[0], report.failed_checks[0].check_id)
        self.assertEqual("/bucket1/bucket2/bucket3/bucket.tf", report.failed_checks[0].file_path)
        self.assertEqual(1, len(report.failed_checks))

        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources", "nested_dir")

        runner = Runner(db_connector=self.db_connector())
        filter = RunnerFilter(framework=['terraform'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.TERRAFORM: Severities[BcSeverities.OFF]}
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
        scan_dir_path = os.path.join(current_dir, "resources", "nested_dir")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))

        scan_dir_path = os.path.join(current_dir, "resources", "nested_dir")
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')
        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "nested_dir", "dir1", "example.tf")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "nested_dir", "dir1", "example.tf")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_definition_context_path(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "definition_context_path_nested_modules")
        checks_allow_list = ['CKV_AWS_20']
        expected_definition_context_paths = [os.path.join(resources_path, 'main.tf'),
                                             f'{os.path.join(resources_path, "module/main.tf")}{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{os.path.join(resources_path, "main.tf")}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}',
                                             f'{os.path.join(resources_path, "module/module2/main.tf")}{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{os.path.join(resources_path, "module/main.tf")}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}{os.path.join(resources_path, "main.tf")}{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}{TERRAFORM_NESTED_MODULE_PATH_ENDING}']
        expected_definition_context_paths.sort()

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=resources_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allow_list))
        definition_context_paths = [f.definition_context_file_path for f in report.failed_checks]
        definition_context_paths.sort()
        self.assertEqual(expected_definition_context_paths.sort(), definition_context_paths.sort())

    def test_runner_malformed_857(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/malformed_857/main.tf"

        runner = Runner(db_connector=self.db_connector())
        runner.run(root_folder=None, external_checks_dir=None, files=[passing_tf_file_path])
        # If we get here all is well. :-)  Failure would throw an exception.

    def test_runner_empty_locals(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/empty_locals"

        runner = Runner(db_connector=self.db_connector())
        r = runner.run(root_folder=passing_tf_file_path, external_checks_dir=None)

        assert len(r.parsing_errors) == 0

    def test_module_skip(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        report = Runner(db_connector=self.db_connector()).run(root_folder=f"{current_dir}/resources/module_skip",
                              external_checks_dir=None,
                              runner_filter=RunnerFilter(checks="CKV_AWS_19"))  # bucket encryption

        self.assertEqual(len(report.skipped_checks), 5)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)

        found_inside = False
        found_outside = False

        for record in report.failed_checks:
            if "inside" in record.resource:
                found_inside = True
                self.assertEqual(record.resource, "module.test_module.aws_s3_bucket.inside")
                assert record.file_path == "/module/module.tf"
                self.assertEqual(record.file_line_range, [7, 9])
                assert record.caller_file_path == "/main.tf"
                # ATTENTION!! If this breaks, see the "HACK ALERT" comment in runner.run_block.
                #             A bug might have been fixed.
                self.assertEqual(record.caller_file_line_range, [6, 8])

            if "outside" in record.resource:
                found_outside = True
                self.assertEqual(record.resource, "aws_s3_bucket.outside")
                assert record.file_path == "/main.tf"
                self.assertEqual(record.file_line_range, [12, 16])
                self.assertIsNone(record.caller_file_path)
                self.assertIsNone(record.caller_file_line_range)

        self.assertFalse(found_inside)
        self.assertFalse(found_outside)

    def test_nested_modules_caller_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        report = Runner(db_connector=self.db_connector()).run(
            root_folder=f"{current_dir}/resources/nested_modules_caller_file",
            external_checks_dir=None,
            runner_filter=RunnerFilter(checks="CKV_AWS_143"))  # bucket encryption
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(len(report.passed_checks), 0)
        record = report.failed_checks[0]
        self.assertIsNotNone(record.caller_file_path)
        self.assertIsNotNone(record.caller_file_line_range)

    def test_module_failure_reporting_772(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        report = Runner(db_connector=self.db_connector()).run(root_folder=f"{current_dir}/resources/module_failure_reporting_772",
                              external_checks_dir=None,
                              runner_filter=RunnerFilter(checks="CKV_AWS_143"))  # bucket encryption

        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(len(report.passed_checks), 0)

        found_inside = False
        found_outside = False
        for record in report.failed_checks:
            # "outside" bucket (not defined in a module) should be a direct resource path and
            # should not have caller file info.
            if "outside" in record.resource:
                found_outside = True
                self.assertEqual(record.resource, "aws_s3_bucket.outside")
                assert record.file_path == "/main.tf"
                self.assertEqual(record.file_line_range, [11, 17])
                self.assertIsNone(record.caller_file_path)
                self.assertIsNone(record.caller_file_line_range)

            if "inside" in record.resource:
                found_inside = True
                self.assertEqual(record.resource, "module.test_module.aws_s3_bucket.inside")
                assert record.file_path == "/module/module.tf"
                self.assertEqual(record.file_line_range, [7, 13])
                assert record.caller_file_path == "/main.tf"
                self.assertEqual(record.caller_file_line_range, [6, 8])

        self.assertTrue(found_inside)
        self.assertTrue(found_outside)

    def test_loading_external_checks_yaml(self):
        runner = Runner(db_connector=self.db_connector())
        runner.graph_registry.checks = []
        runner.graph_registry.load_checks()
        base_len = len(runner.graph_registry.checks)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_path = current_dir + "/extra_yaml_checks"
        runner.load_external_checks([extra_checks_dir_path])
        self.assertEqual(len(runner.graph_registry.checks), base_len + 5)
        runner.graph_registry.checks = runner.graph_registry.checks[:base_len]

    def test_loading_external_checks_yaml_multiple_times(self):
        runner = Runner(db_connector=self.db_connector())
        current_dir = os.path.dirname(os.path.realpath(__file__))
        runner.graph_registry.checks = []
        extra_checks_dir_path = [current_dir + "/extra_yaml_checks"]
        runner.load_external_checks(extra_checks_dir_path)
        self.assertEqual(len(runner.graph_registry.checks), 5)
        runner.load_external_checks(extra_checks_dir_path)
        self.assertEqual(len(runner.graph_registry.checks), 5)

        graph_checks = [x.id for x in runner.graph_registry.checks]
        self.assertIn('CUSTOM_GRAPH_AWS_1', graph_checks)
        self.assertIn('CUSTOM_GRAPH_AWS_2', graph_checks)
        self.assertIn('CKV2_CUSTOM_1', graph_checks)
        runner.graph_registry.checks = []

    def test_loading_external_checks_python(self):
        runner = Runner(db_connector=self.db_connector())
        from tests.terraform.runner.extra_checks.S3EnvironmentCheck import scanner
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_paths = [current_dir + "/extra_checks"]
        runner.load_external_checks(extra_checks_dir_paths)
        found = 0
        for resource_type in scanner.supported_resources:
            checks = resource_registry.checks[resource_type]
            checks_ids = [c.id for c in checks]
            self.assertIn(scanner.id, checks_ids)
            found += 1
        self.assertEqual(found, len(scanner.supported_resources))

    def test_loading_external_checks_python_multiple_times(self):
        runner = Runner(db_connector=self.db_connector())
        from tests.terraform.runner.extra_checks.S3EnvironmentCheck import scanner
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_paths = [current_dir + "/extra_checks", current_dir + "/extra_checks"]
        runner.load_external_checks(extra_checks_dir_paths)
        found = 0
        for resource_type in scanner.supported_resources:
            checks = resource_registry.checks[resource_type]
            checks_ids = [c.id for c in checks]
            self.assertIn(scanner.id, checks_ids)
            instances = list(filter(lambda c: c.id == scanner.id, checks))
            self.assertEqual(len(instances), 1)
            found += 1

        self.assertEqual(found, len(scanner.supported_resources))

    def test_loading_external_checks_python_and_yaml(self):
        runner = Runner(db_connector=self.db_connector())
        from tests.terraform.runner.extra_checks.S3EnvironmentCheck import scanner
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_paths = [current_dir + "/extra_checks", current_dir + "/extra_yaml_checks"]
        runner.load_external_checks(extra_checks_dir_paths)
        found = 0
        for resource_type in scanner.supported_resources:
            checks = resource_registry.checks[resource_type]
            checks_ids = [c.id for c in checks]
            self.assertIn(scanner.id, checks_ids)
            found += 1
        self.assertEqual(found, len(scanner.supported_resources))
        self.assertEqual(len(list(filter(lambda c: c.id == CUSTOM_GRAPH_CHECK_ID, runner.graph_registry.checks))), 1)
        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_wrong_check_imports(self):
        wrong_imports = ("checkov.arm", "checkov.cloudformation", "checkov.dockerfile", "checkov.helm", "checkov.kubernetes", "checkov.serverless")
        check_imports = []

        checks_path = Path(inspect.getfile(Runner)).parent.joinpath("checks")
        for file in checks_path.rglob("*.py"):
            with file.open() as f:
                instructions = dis.get_instructions(f.read())
                import_names = [instr.argval for instr in instructions if "IMPORT_NAME" == instr.opname]

                for import_name in import_names:
                    if import_name.startswith(wrong_imports):
                        check_imports.append({file.name: import_name})

        assert len(check_imports) == 0, f"Wrong imports were added: {check_imports}"

    def test_entity_context_fetching(self):
        runner = Runner(db_connector=self.db_connector())
        runner.context = {'/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf': {'module': {'module': {'vpc': {'start_line': 1, 'end_line': 7, 'code_lines': [(1, 'module "vpc" {\n'), (2, '  source       = "../../"\n'), (3, '  cidr         = var.cidr\n'), (4, '  zone         = var.zone\n'), (5, '  common_tags  = var.common_tags\n'), (6, '  account_name = var.account_name\n'), (7, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/example/examplea/provider.aws.tf': {'provider': {'aws': {'default': {'start_line': 1, 'end_line': 3, 'code_lines': [(1, 'provider "aws" {\n'), (2, '  region = "eu-west-2"\n'), (3, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/example/examplea/variables.tf': {'variable': {'cidr': {'start_line': 1, 'end_line': 3, 'code_lines': [(1, 'variable "cidr" {\n'), (2, '  type = string\n'), (3, '}\n')], 'skipped_checks': []}, 'zone': {'start_line': 5, 'end_line': 7, 'code_lines': [(5, 'variable "zone" {\n'), (6, '  type = list(any)\n'), (7, '}\n')], 'skipped_checks': []}, 'account_name': {'start_line': 9, 'end_line': 11, 'code_lines': [(9, 'variable "account_name" {\n'), (10, '  type = string\n'), (11, '}\n')], 'skipped_checks': []}, 'common_tags': {'start_line': 13, 'end_line': 15, 'code_lines': [(13, 'variable "common_tags" {\n'), (14, '  type = map(any)\n'), (15, '}\n')], 'skipped_checks': []}}}, f'/mock/os/terraform-aws-vpc/aws_eip.nateip.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_eip': {'nateip': {'start_line': 1, 'end_line': 4, 'code_lines': [(1, 'resource "aws_eip" "nateip" {\n'), (2, '  count = var.subnets\n'), (3, '  tags  = var.common_tags\n'), (4, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_internet_gateway.gw.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_internet_gateway': {'gw': {'start_line': 1, 'end_line': 6, 'code_lines': [(1, 'resource "aws_internet_gateway" "gw" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  tags = merge(var.common_tags,\n'), (5, '  tomap({ "Name" = "${upper(var.account_name)}-IGW" }))\n'), (6, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_nat_gateway.natgateway.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_nat_gateway': {'natgateway': {'start_line': 1, 'end_line': 8, 'code_lines': [(1, 'resource "aws_nat_gateway" "natgateway" {\n'), (2, '  count         = var.subnets\n'), (3, '  allocation_id = element(aws_eip.nateip.*.id, count.index)\n'), (4, '  depends_on    = [aws_internet_gateway.gw]\n'), (5, '  subnet_id     = element(aws_subnet.public.*.id, count.index)\n'), (6, '  tags = merge(var.common_tags,\n'), (7, '  tomap({ "Name" = "${upper(var.account_name)}-AZ${count.index + 1}" }))\n'), (8, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_network_acl.NetworkAclPrivate.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_network_acl': {'networkaclprivate': {'start_line': 1, 'end_line': 25, 'code_lines': [(1, 'resource "aws_network_acl" "networkaclprivate" {\n'), (2, '  vpc_id     = aws_vpc.main.id\n'), (3, '  subnet_ids = aws_subnet.private.*.id\n'), (4, '\n'), (5, '  egress {\n'), (6, '    rule_no    = 100\n'), (7, '    action     = "allow"\n'), (8, '    cidr_block = "0.0.0.0/0"\n'), (9, '    from_port  = 0\n'), (10, '    to_port    = 0\n'), (11, '    protocol   = "all"\n'), (12, '  }\n'), (13, '\n'), (14, '  ingress {\n'), (15, '    rule_no    = 100\n'), (16, '    action     = "allow"\n'), (17, '    cidr_block = "0.0.0.0/0"\n'), (18, '    from_port  = 0\n'), (19, '    to_port    = 0\n'), (20, '    protocol   = "all"\n'), (21, '  }\n'), (22, '\n'), (23, '  tags = merge(var.common_tags,\n'), (24, '  tomap({ "Name" = "${var.account_name}-NetworkAcl-Private" }))\n'), (25, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_network_acl.NetworkAclPublic.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_network_acl': {'networkaclpublic': {'start_line': 1, 'end_line': 25, 'code_lines': [(1, 'resource "aws_network_acl" "networkaclpublic" {\n'), (2, '  vpc_id     = aws_vpc.main.id\n'), (3, '  subnet_ids = aws_subnet.public.*.id\n'), (4, '\n'), (5, '  egress {\n'), (6, '    rule_no    = 100\n'), (7, '    action     = "allow"\n'), (8, '    cidr_block = "0.0.0.0/0"\n'), (9, '    from_port  = 0\n'), (10, '    to_port    = 0\n'), (11, '    protocol   = "all"\n'), (12, '  }\n'), (13, '\n'), (14, '  ingress {\n'), (15, '    rule_no    = 100\n'), (16, '    action     = "allow"\n'), (17, '    cidr_block = "0.0.0.0/0"\n'), (18, '    from_port  = 0\n'), (19, '    to_port    = 0\n'), (20, '    protocol   = "all"\n'), (21, '  }\n'), (22, '\n'), (23, '  tags = merge(var.common_tags,\n'), (24, '  tomap({ "Name" = "${var.account_name}-NetworkAcl-Public" }))\n'), (25, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_route_table.private.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_route_table': {'private': {'start_line': 1, 'end_line': 8, 'code_lines': [(1, 'resource "aws_route_table" "private" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  propagating_vgws = [aws_vpn_gateway.vpn_gw.id]\n'), (5, '\n'), (6, '  tags = merge(var.common_tags,\n'), (7, '  tomap({ "Name" = "${var.account_name}-Private-${element(aws_subnet.private.*.id, 0)}" }))\n'), (8, '}\n')], 'skipped_checks': []}}, 'aws_route': {'private': {'start_line': 10, 'end_line': 14, 'code_lines': [(10, 'resource "aws_route" "private" {\n'), (11, '  route_table_id         = aws_route_table.private.id\n'), (12, '  destination_cidr_block = "0.0.0.0/0"\n'), (13, '  nat_gateway_id         = element(aws_nat_gateway.natgateway.*.id, 0)\n'), (14, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_route_table.public.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_route_table': {'public': {'start_line': 1, 'end_line': 6, 'code_lines': [(1, 'resource "aws_route_table" "public" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  tags = merge(var.common_tags,\n'), (5, '  tomap({ "Name" = "${upper(var.account_name)}-Public" }))\n'), (6, '}\n')], 'skipped_checks': []}}, 'aws_route': {'public': {'start_line': 8, 'end_line': 12, 'code_lines': [(8, 'resource "aws_route" "public" {\n'), (9, '  route_table_id         = aws_route_table.public.id\n'), (10, '  destination_cidr_block = "0.0.0.0/0"\n'), (11, '  gateway_id             = aws_internet_gateway.gw.id\n'), (12, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_route_table_association.private.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_route_table_association': {'private': {'start_line': 1, 'end_line': 5, 'code_lines': [(1, 'resource "aws_route_table_association" "private" {\n'), (2, '  count          = var.subnets\n'), (3, '  subnet_id      = element(aws_subnet.private.*.id, count.index)\n'), (4, '  route_table_id = aws_route_table.private.id\n'), (5, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_route_table_association.public.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_route_table_association': {'public': {'start_line': 1, 'end_line': 5, 'code_lines': [(1, 'resource "aws_route_table_association" "public" {\n'), (2, '  count          = var.subnets\n'), (3, '  subnet_id      = element(aws_subnet.public.*.id, count.index)\n'), (4, '  route_table_id = aws_route_table.public.id\n'), (5, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_subnet.private.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_subnet': {'private': {'start_line': 1, 'end_line': 10, 'code_lines': [(1, 'resource "aws_subnet" "private" {\n'), (2, '  count             = var.subnets\n'), (3, '  vpc_id            = aws_vpc.main.id\n'), (4, '  cidr_block        = local.private_cidrs[count.index]\n'), (5, '  availability_zone = data.aws_availability_zones.available.names[count.index]\n'), (6, '\n'), (7, '  tags = merge(var.common_tags,\n'), (8, '    tomap({ "Type" = "Private" }),\n'), (9, '  tomap({ "Name" = "${upper(var.account_name)}-Private-${var.zone[count.index]}" }))\n'), (10, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_subnet.public.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_subnet': {'public': {'start_line': 1, 'end_line': 10, 'code_lines': [(1, 'resource "aws_subnet" "public" {\n'), (2, '  count             = var.subnets\n'), (3, '  vpc_id            = aws_vpc.main.id\n'), (4, '  cidr_block        = local.public_cidrs[count.index]\n'), (5, '  availability_zone = data.aws_availability_zones.available.names[count.index]\n'), (6, '\n'), (7, '  tags = merge(var.common_tags,\n'), (8, '    tomap({ "Type" = "Public" }),\n'), (9, '  tomap({ "Name" = "${upper(var.account_name)}-Public-${var.zone[count.index]}" }))\n'), (10, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_vpc.main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'locals': {'start_line': 10, 'end_line': 12, 'code_lines': [(10, 'locals {\n'), (11, '  tags = merge(var.common_tags, tomap({ "Name" = upper(var.account_name) }))\n'), (12, '}\n')], 'assignments': {'tags': "merge([],tomap({'Name':'upper(test)'}))"}, 'skipped_checks': []}, 'resource': {'aws_vpc': {'main': {'start_line': 1, 'end_line': 7, 'code_lines': [(1, 'resource "aws_vpc" "main" {\n'), (2, '  cidr_block           = var.cidr\n'), (3, '  enable_dns_support   = true\n'), (4, '  enable_dns_hostnames = true\n'), (5, '\n'), (6, '  tags = local.tags\n'), (7, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/aws_vpn_gateway.vpn_gw.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'resource': {'aws_vpn_gateway': {'vpn_gw': {'start_line': 1, 'end_line': 6, 'code_lines': [(1, 'resource "aws_vpn_gateway" "vpn_gw" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  tags = merge(var.common_tags,\n'), (5, '  tomap({ "Name" = "${upper(var.account_name)}-VGW" }))\n'), (6, '}\n')], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/data.aws_availability_zones.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'data': {'aws_availability_zones': {'available': {'start_line': 1, 'end_line': 0, 'code_lines': [], 'skipped_checks': []}}}}, f'/mock/os/terraform-aws-vpc/variables.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}': {'locals': {'start_line': 27, 'end_line': 30, 'code_lines': [(27, 'locals {\n'), (28, '  public_cidrs  = [cidrsubnet(var.cidr, 3, 0), cidrsubnet(var.cidr, 3, 1), cidrsubnet(var.cidr, 3, 2)]\n'), (29, '  private_cidrs = [cidrsubnet(var.cidr, 3, 3), cidrsubnet(var.cidr, 3, 4), cidrsubnet(var.cidr, 3, 5)]\n'), (30, '}\n')], 'skipped_checks': []}, 'variable': {'account_name': {'start_line': 1, 'end_line': 4, 'code_lines': [(1, 'variable "account_name" {\n'), (2, '  type        = string\n'), (3, '  description = "The Name of the Account"\n'), (4, '}\n')], 'skipped_checks': []}, 'cidr': {'start_line': 6, 'end_line': 9, 'code_lines': [(6, 'variable "cidr" {\n'), (7, '  type        = string\n'), (8, '  description = "The range to be associated with the VPC and cleaved into the subnets"\n'), (9, '}\n')], 'skipped_checks': []}, 'common_tags': {'start_line': 11, 'end_line': 14, 'code_lines': [(11, 'variable "common_tags" {\n'), (12, '  type        = map(any)\n'), (13, '  description = "A tagging scheme"\n'), (14, '}\n')], 'skipped_checks': []}, 'zone': {'start_line': 16, 'end_line': 19, 'code_lines': [(16, 'variable "zone" {\n'), (17, '  type        = list(any)\n'), (18, '  description = "Availability zone names"\n'), (19, '}\n')], 'skipped_checks': []}, 'subnets': {'start_line': 21, 'end_line': 25, 'code_lines': [(21, 'variable "subnets" {\n'), (22, '  type        = number\n'), (23, '  default     = 3\n'), (24, '  description = "The number of subnets required, less than or equal to the number of availability zones"\n'), (25, '}\n')], 'skipped_checks': []}, 'assignments': {'subnets': 3}}}}
        entity_with_non_found_path = {'block_name_': 'aws_vpc.main', 'block_type_': 'resource', 'file_path_': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf', 'config_': {'aws_vpc': {'main': {'cidr_block': ['10.0.0.0/21'], 'enable_dns_hostnames': [True], 'enable_dns_support': [True], 'tags': ["merge([],tomap({'Name':'upper(test)'}))"]}}}, 'label_': 'BlockType.RESOURCE: aws_vpc.main', 'id_': 'aws_vpc.main', 'source_': 'Terraform', 'cidr_block': '10.0.0.0/21', 'enable_dns_hostnames': True, 'enable_dns_support': True, 'tags': "merge([],tomap({'Name':'upper(test)'}))", 'resource_type': 'aws_vpc', 'rendering_breadcrumbs_': {'cidr_block': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'cidr', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'output', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/outputs.tf', 'module_connection': False}], 'source_module_': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf'}], 'tags': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'account_name', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'tags', 'path': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf', 'module_connection': False}]}, 'hash': 'bac3bb7d21610be9ad786c1e9b5a2b3f6f13e60699fa935b32bb1f9f10a792e4', 'module_dependency_': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_dependency_num_': '0'}
        entity_context = runner.get_entity_context_and_evaluations(entity_with_non_found_path)

        assert entity_context is not None
        assert entity_context['start_line'] == 1 and entity_context['end_line'] == 7

        entity_with_found_path = {'block_name_': 'aws_vpc.main', 'block_type_': 'resource', 'file_path_': f'/mock/os/terraform-aws-vpc/aws_vpc.main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}', 'config_': {'aws_vpc': {'main': {'cidr_block': ['10.0.0.0/21'], 'enable_dns_hostnames': [True], 'enable_dns_support': [True], 'tags': ["merge([],tomap({'Name':'upper(test)'}))"]}}}, 'label_': 'BlockType.RESOURCE: aws_vpc.main', 'id_': 'aws_vpc.main', 'source_': 'Terraform', 'cidr_block': '10.0.0.0/21', 'enable_dns_hostnames': True, 'enable_dns_support': True, 'tags': "merge([],tomap({'Name':'upper(test)'}))", 'resource_type': 'aws_vpc', 'rendering_breadcrumbs_': {'cidr_block': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'cidr', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'output', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/outputs.tf', 'module_connection': False}], 'source_module_': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf'}], 'tags': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'account_name', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'tags', 'path': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf', 'module_connection': False}]}, 'hash': 'bac3bb7d21610be9ad786c1e9b5a2b3f6f13e60699fa935b32bb1f9f10a792e4'}
        entity_context = runner.get_entity_context_and_evaluations(entity_with_found_path)

        assert entity_context is not None
        assert entity_context['start_line'] == 1 and entity_context['end_line'] == 7

    def test_resource_ids_nested_modules(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_ids_nested_modules")
        checks_allow_list = ['CKV_AWS_20']
        expected_resources_ids = ['aws_s3_bucket.example', 'module.s3_module.aws_s3_bucket.example2',
                                  'module.s3_module.module.inner_s3_module.aws_s3_bucket.example3']
        expected_resources_ids.sort()

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=resources_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"], checks=checks_allow_list))

        resources_ids = [f.resource for f in report.failed_checks]
        resources_ids.sort()
        self.assertEqual(len(resources_ids), 3)
        self.assertEqual(expected_resources_ids, resources_ids)

    def test_resource_values_dont_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_value_without_var")
        checks_allow_list = ['CKV_AWS_21']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework=["terraform"],
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(len(report.failed_checks), 1)

    def test_resource_values_do_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_value_without_var")
        checks_allow_list = ['CKV_AWS_21']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf", "variables_unscoped.tf"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework=["terraform"],
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(len(report.failed_checks), 3)

    def test_resource_negative_values_dont_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_negative_value_without_var")
        checks_allow_list = ['CKV_AWS_57']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform',
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(len(report.failed_checks), 1)

    def test_resource_negative_values_do_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_negative_value_without_var")
        checks_allow_list = ['CKV_AWS_57']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf", "variables_unscoped.tf"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework=["terraform"],
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(len(report.failed_checks), 3)

    def test_unrendered_simple_var(self):
        resources_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "unrendered_vars")
        file_to_scan = os.path.join(resources_dir, "simple.tf")
        checks = ['BUCKET_EQUALS', 'BUCKET_EXISTS']

        runner = Runner(db_connector=self.db_connector())
        runner_filter = RunnerFilter(framework=['terraform'], checks=checks)
        report = runner.run(root_folder=None, files=[file_to_scan], external_checks_dir=[resources_dir], runner_filter=runner_filter)

        # plus 1 unknown
        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(len(report.failed_checks), 0)

        self.assertTrue(any(r.check_id == 'BUCKET_EXISTS' and r.resource == 'aws_s3_bucket.known_simple_pass' for r in report.passed_checks))
        self.assertTrue(any(r.check_id == 'BUCKET_EQUALS' and r.resource == 'aws_s3_bucket.known_simple_pass' for r in report.passed_checks))

        self.assertTrue(any(r.check_id == 'BUCKET_EXISTS' and r.resource == 'aws_s3_bucket.unknown_simple' for r in report.passed_checks))

    def test_unrendered_nested_var(self):
        resources_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "unrendered_vars")
        file_to_scan = os.path.join(resources_dir, "nested.tf")
        checks = ['COMPONENT_EQUALS', 'COMPONENT_EXISTS']

        runner = Runner(db_connector=self.db_connector())
        runner_filter = RunnerFilter(framework=['terraform'], checks=checks)
        report = runner.run(root_folder=None, files=[file_to_scan], external_checks_dir=[resources_dir], runner_filter=runner_filter)

        # plus 3 unknown
        self.assertEqual(len(report.passed_checks), 5)
        self.assertEqual(len(report.failed_checks), 2)

        self.assertTrue(any(r.check_id == 'COMPONENT_EXISTS' and r.resource == 'aws_s3_bucket.unknown_nested_2_pass' for r in report.passed_checks))

        self.assertTrue(any(r.check_id == 'COMPONENT_EXISTS' and r.resource == 'aws_s3_bucket.known_nested_pass' for r in report.passed_checks))
        self.assertTrue(any(r.check_id == 'COMPONENT_EQUALS' and r.resource == 'aws_s3_bucket.known_nested_pass' for r in report.passed_checks))

        self.assertTrue(any(r.check_id == 'COMPONENT_EXISTS' and r.resource == 'aws_s3_bucket.known_nested_2_pass' for r in report.passed_checks))
        self.assertTrue(any(r.check_id == 'COMPONENT_EQUALS' and r.resource == 'aws_s3_bucket.known_nested_2_pass' for r in report.passed_checks))

        self.assertTrue(any(r.check_id == 'COMPONENT_EXISTS' and r.resource == 'aws_s3_bucket.known_nested_fail' for r in report.failed_checks))
        self.assertTrue(any(r.check_id == 'COMPONENT_EQUALS' and r.resource == 'aws_s3_bucket.known_nested_fail' for r in report.failed_checks))

    def test_no_duplicate_results(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "duplicate_violations")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=resources_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"]))

        unique_checks = []
        for record in report.passed_checks:
            check_unique = f"{record.check_id}.{record.resource}"
            if check_unique in unique_checks:
                self.fail(f"found duplicate results in report: {record.to_string()}")
            unique_checks.append(check_unique)

    def test_malformed_file_in_parsing_error(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "unbalanced_eval_brackets")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=resources_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform'))
        file_path = os.path.join(resources_path, 'main.tf')
        self.assertEqual(report.parsing_errors[0], file_path)

    def test_runner_scan_hcl(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        dir_to_scan = os.path.join(current_dir, 'resources', 'tf_with_hcl_files')
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=dir_to_scan, external_checks_dir=None, files=None)
        self.assertEqual(len(report.resources), 2)

    def test_runner_scan_hcl_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        file_to_scan = os.path.join(current_dir, 'resources', 'tf_with_hcl_files', 'example_acl_fail.hcl')

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_to_scan])
        self.assertEqual(len(report.resources), 1)

    def test_runner_exclude_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        path_to_scan = os.path.join(current_dir, 'resources', 'nested_dir', 'dir1')
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=path_to_scan, external_checks_dir=None, runner_filter=RunnerFilter(framework=["terraform"], excluded_paths=['example.tf']))
        self.assertEqual(0, len(report.resources))

    def test_runner_exclude_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        path_to_scan = os.path.join(current_dir, 'resources', 'nested_dir')
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=path_to_scan, external_checks_dir=None, runner_filter=RunnerFilter(framework=["terraform"], excluded_paths=['dir1']))
        self.assertEqual(1, len(report.resources))

    def test_runner_merge_operator(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/merge_operator"
        extra_checks_dir_path = [current_dir + "/resources/merge_operator/query"]

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=extra_checks_dir_path, runner_filter=RunnerFilter(checks=["CKV2_AWS_200"]))

        self.assertEqual(1, len(report.passed_checks))

    def test_record_includes_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_s3_bucket"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "valid_tf_only_failed_checks", "example_acl_fail.tf")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['terraform'], checks=[custom_check_id])
        )

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_severity_check_filter_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_s3_bucket"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources",
                                      "valid_tf_only_failed_checks", "example_acl_fail.tf")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['terraform'], checks=['MEDIUM'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    @mock.patch("checkov.common.runners.base_runner.ignored_directories", ['dir1'])
    def test_runner_ignore_dirs(self):
        """CKV_IGNORED_DIRECTORIES='dir1' and CKV_IGNORE_HIDDEN_DIRECTORIES=True (default)"""
        report = self.scan_hidden_dir()
        self.assertEqual(len(report.resources), 1)

    @mock.patch("checkov.common.runners.base_runner.ignored_directories", ['dir1'])
    @mock.patch("checkov.common.runners.base_runner.IGNORE_HIDDEN_DIRECTORY_ENV", 0)
    def test_runner_scan_hidden_dirs_and_ignore_dirs(self):
        """CKV_IGNORED_DIRECTORIES='dir1' and CKV_IGNORE_HIDDEN_DIRECTORIES=False"""
        report = self.scan_hidden_dir()
        self.assertEqual(len(report.resources), 3)

    def test_runner_scan_default_env_vars(self):
        """CKV_IGNORED_DIRECTORIES and CKV_IGNORE_HIDDEN_DIRECTORIES are equal to default"""
        report = self.scan_hidden_dir()
        self.assertEqual(len(report.resources), 2)

    @mock.patch("checkov.common.runners.base_runner.IGNORE_HIDDEN_DIRECTORY_ENV", 0)
    def test_runner_scan_hidden_dirs(self):
        """CKV_IGNORE_HIDDEN_DIRECTORIES=False and CKV_IGNORED_DIRECTORIES equals to default value"""
        report = self.scan_hidden_dir()
        self.assertEqual(len(report.resources), 5)

    def scan_hidden_dir(self):
        """ scan resources/hidden_dir directory."""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        path_to_scan = os.path.join(current_dir, 'resources', 'hidden_dir')
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=path_to_scan, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=["terraform"]))
        return report

    def test_severity_check_filter(self):
        custom_check_id = "MY_CUSTOM_CHECK"


        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_s3_bucket"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.MEDIUM]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources",
                                      "valid_tf_only_failed_checks", "example_acl_fail.tf")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['terraform'], checks=['MEDIUM'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_skip_check_filter_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"


        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_s3_bucket"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources",
                                      "valid_tf_only_failed_checks", "example_acl_fail.tf")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['terraform'], skip_checks=['MEDIUM'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_skip_check_filter_include(self):
        custom_check_id = "MY_CUSTOM_CHECK"


        resource_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["aws_s3_bucket"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources",
                                      "valid_tf_only_failed_checks", "example_acl_fail.tf")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['terraform'], skip_checks=['MEDIUM'])
        )

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def tearDown(self):
        parser_registry.context = {}
        resource_registry.checks = self.orig_checks

    @parameterized.expand([
        (NetworkxConnector,),
        (IgraphConnector,)
    ])
    def test_get_graph_resource_entity_config(self, graph_connector):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        path_to_scan = os.path.join(current_dir, 'resources', 'get_graph_resource_entity_config')
        graph_manager = TerraformGraphManager(db_connector=graph_connector())
        graph, _ = graph_manager.build_graph_from_source_directory(path_to_scan)
        graph_manager.save_graph(graph)
        graph_connector = graph_manager.get_reader_endpoint()
        if isinstance(graph_connector, DiGraph):
            for _, data in graph_connector.nodes(data=True):
                config = Runner.get_graph_resource_entity_config(data)
                self.assertIn(CustomAttributes.TF_RESOURCE_ADDRESS, config)
        if isinstance(graph_connector, Graph):
            for data in graph_connector.vs.select()["attr"]:
                config = Runner.get_graph_resource_entity_config(data)
                self.assertIn(CustomAttributes.TF_RESOURCE_ADDRESS, config)

    @mock.patch.dict(os.environ, {"ENABLE_DEFINITION_KEY": "True"})
    def test_entity_context_fetching_with_TFDefinitionKey(self):
        runner = Runner(db_connector=self.db_connector())
        full_file_path = TFDefinitionKey(file_path='/tmp/checkov/1069803756901857280/prisma-new-user/TestAutomationRepo_7-30-2023-1-38-24-PM/pr/4/58a43cb0e5daee00398b6c892c9287438c7c74ea/diff/src/file1.tf', tf_source_modules=None)
        runner.context = {full_file_path: {'resource': {'aws_lb_listener': {'https1': {'start_line': 1, 'end_line': 7, 'code_lines': [[1, 'resource "aws_lb_listener" "https1" {\n'], [2, '  load_balancer_arn = ""\n'], [3, '  protocol          = "HTTPS"\n'], [4, '  default_action {\n'], [5, '    type = ""\n'], [6, '  }\n'], [7, '}']], 'skipped_checks': []}}}}}
        entity_with_found_path = {'block_name_': 'aws_lb_listener.https1', 'block_type_': 'resource', 'file_path_': '/tmp/checkov/1069803756901857280/prisma-new-user/TestAutomationRepo_7-30-2023-1-38-24-PM/pr/4/58a43cb0e5daee00398b6c892c9287438c7c74ea/diff/src/file1.tf', 'config_': {'aws_lb_listener': {'https1': {'__end_line__': 7, '__start_line__': 1, 'default_action': [{'type': ['']}], 'load_balancer_arn': [''], 'protocol': ['HTTPS'], '__address__': 'aws_lb_listener.https1'}}}, 'attributes_': {'__end_line__': 7, '__start_line__': 1, 'default_action': {'type': ''}, 'load_balancer_arn': [''], 'protocol': ['HTTPS'], 'resource_type': ['aws_lb_listener'], 'default_action.type': '', '__address__': 'aws_lb_listener.https1'}, 'label_': 'resource: aws_lb_listener.https1', 'id_': 'aws_lb_listener.https1', 'customer_name_': '1069803756901857280', 'account_id_': 'prisma-new-user/TestAutomationRepo_7-30-2023-1-38-24-PM/CICD/243676', 'unique_tag_': 'prod', 'source_': 'terraform', 'violations_count_': 0, 'region_': '', '__end_line__': 7, '__start_line__': 1, 'default_action': {'type': ''}, 'default_action.type': '', 'load_balancer_arn': '', 'protocol': 'HTTPS', 'resource_type': 'aws_lb_listener', '__address__': 'aws_lb_listener.https1', 'module_dependency_': '', 'module_dependency_num_': '', 'hash': 'd61bc3a35537776896f83679a51e63d3a6074f66b368bc4fea07871d282875e9'}
        entity_context = runner.get_entity_context_and_evaluations(entity_with_found_path)
        assert entity_context is not None
        assert entity_context['start_line'] == 1 and entity_context['end_line'] == 7


if __name__ == '__main__':
    unittest.main()
