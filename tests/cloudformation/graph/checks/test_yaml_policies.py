import copy
import json
import os
import unittest
import warnings
from pathlib import Path
from typing import List

import yaml

from checkov.cloudformation import checks
from checkov.cloudformation.graph_manager import CloudformationGraphManager
from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter


class TestYamlPolicies(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_SagemakerNotebookEncryption(self):
        self.go("SagemakerNotebookEncryption")

    def test_MSKClusterLogging(self):
        self.go("MSKClusterLogging")

    def test_LambdaFunction(self):
        self.go("LambdaFunction")

    def test_registry_load(self):
        registry = get_checks_registry()
        self.assertGreater(len(registry.checks), 0)

    def go(self, dir_name, check_name=None):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                f"resources/{dir_name}")
        assert os.path.exists(dir_path)
        policy_dir_path = os.path.dirname(checks.__file__)
        assert os.path.exists(policy_dir_path)
        found = False
        for root, d_names, f_names in os.walk(policy_dir_path):
            for f_name in f_names:
                check_name = dir_name if check_name is None else check_name
                if f_name == f"{check_name}.yaml":
                    found = True
                    policy = load_yaml_data(f_name, root)
                    assert policy is not None
                    expected = load_yaml_data("expected.yaml", dir_path)
                    assert expected is not None
                    report = get_policy_results(dir_path, policy)
                    expected = load_yaml_data("expected.yaml", dir_path)

                    expected_to_fail = expected.get('fail', [])
                    expected_to_pass = expected.get('pass', [])
                    expected_to_skip = expected.get('skip', [])
                    self.assert_entities(expected_to_pass, report.passed_checks, True)
                    self.assert_entities(expected_to_fail, report.failed_checks, False)
                    self.assert_entities(expected_to_skip, report.skipped_checks, True)

        assert found

    def assert_entities(self, expected_entities: List[str], results: List[Record], assertion: bool):
        self.assertEqual(len(expected_entities), len(results),
                         f"mismatch in number of results in {'passed' if assertion else 'failed'}, "
                         f"expected: {len(expected_entities)}, got: {len(results)}")
        for expected_entity in expected_entities:
            found = False
            for check_result in results:
                entity_id = check_result.resource
                if entity_id == expected_entity:
                    found = True
                    break
            self.assertTrue(found, f"expected to find entity {expected_entity}, {'passed' if assertion else 'failed'}")


def get_checks_registry():
    registry = Registry(parser=NXGraphCheckParser(), checks_dir=str(
        Path(
            __file__).parent.parent.parent.parent.parent / "checkov" / "cloudformation" / "checks" / "graph_checks"))
    registry.load_checks()
    return registry


def get_policy_results(root_folder, policy):
    check_id = policy['metadata']['id']
    graph_manager = CloudformationGraphManager(db_connector=NetworkxConnector())
    local_graph, _ = graph_manager.build_graph_from_source_directory(root_folder)
    nx_graph = graph_manager.save_graph(local_graph)
    registry = get_checks_registry()
    checks_results = registry.run_checks(nx_graph, RunnerFilter(checks=[check_id]))
    return create_report_from_graph_checks_results(checks_results, policy['metadata'])


def create_report_from_graph_checks_results(checks_results, check):
    report = Report("cloudformation")
    first_results_key = list(checks_results.keys())[0]
    for check_result in checks_results[first_results_key]:
        entity = check_result["entity"]
        record = Record(check_id=check['id'],
                        check_name=check['name'],
                        check_result=copy.deepcopy(check_result),
                        code_block="",
                        file_path=entity.get(CustomAttributes.FILE_PATH),
                        file_line_range=[entity.get('__startline__'), entity.get('__endline__')],
                        resource=entity.get(CustomAttributes.BLOCK_NAME),
                        entity_tags=entity.get('tags', {}),
                        evaluations=None,
                        check_class=None,
                        file_abs_path=entity.get(CustomAttributes.FILE_PATH))
        if check_result["result"] == CheckResult.PASSED:
            report.passed_checks.append(record)
        if check_result["result"] == CheckResult.FAILED:
            report.failed_checks.append(record)
    return report


def wrap_policy(policy):
    policy['query'] = policy['definition']
    del policy['definition']


def load_yaml_data(source_file_name, dir_path):
    expected_path = os.path.join(dir_path, source_file_name)
    if not os.path.exists(expected_path):
        return None

    with open(expected_path, "r") as f:
        expected_data = yaml.safe_load(f)

    return json.loads(json.dumps(expected_data))
