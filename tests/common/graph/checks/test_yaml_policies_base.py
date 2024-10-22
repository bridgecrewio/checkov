from __future__ import annotations

import itertools
import json
import os
from pathlib import Path

import yaml
from abc import abstractmethod
from typing import List, Optional, Any
from unittest import TestCase

from checkov.cloudformation.runner import Runner
from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.common.graph.graph_manager import GraphManager
from checkov.common.output.record import Record
from checkov.runner_filter import RunnerFilter


class TestYamlPoliciesBase(TestCase):
    def __init__(self, graph_manager: GraphManager, real_graph_checks_path: str,
                 test_checks_path: Optional[str], check_type: str, test_file_path: str,
                 args):
        super().__init__(args)
        self.check_type = check_type
        self.real_graph_checks_path = real_graph_checks_path
        self.checks_dir = test_checks_path
        self.test_file_path = test_file_path
        self.graph_manager = graph_manager

    def go(self, dir_name, check_name=None, local_graph_class=None):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(self.test_file_path)),
                                f"resources/{dir_name}")
        assert os.path.exists(dir_path)
        if self.checks_dir:
            assert os.path.exists(self.checks_dir)
        found = False
        for root, d_names, f_names in itertools.chain(os.walk(self.real_graph_checks_path), os.walk(self.checks_dir)):
            for f_name in f_names:
                check_name = dir_name if check_name is None else check_name
                if f_name == f"{check_name}.yaml":
                    found = True
                    policy = load_yaml_data(f_name, root)
                    assert policy is not None
                    expected = load_yaml_data("expected.yaml", dir_path)
                    assert expected is not None
                    report = self.get_policy_results(dir_path, policy, local_graph_class)
                    expected = load_yaml_data("expected.yaml", dir_path)

                    expected_to_fail = expected.get('fail', [])
                    expected_to_pass = expected.get('pass', [])
                    expected_to_skip = expected.get('skip', [])
                    expected_evaluated_keys = expected.get('evaluated_keys', [])
                    self.assert_entities(expected_to_pass, report.passed_checks, True)
                    self.assert_entities(expected_to_fail, report.failed_checks, False)
                    self.assert_entities(expected_to_skip, report.skipped_checks, True)
                    self.assert_evaluated_keys(expected_evaluated_keys, report.passed_checks + report.failed_checks)

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

    def get_policy_results(self, root_folder, policy, local_graph_class=None):
        check_id = policy['metadata']['id']
        local_graph, _ = self.graph_manager.build_graph_from_source_directory(
            source_dir=root_folder,
            local_graph_class=local_graph_class,
        )
        graph = self.graph_manager.save_graph(local_graph)
        registry = self.get_checks_registry()
        checks_results = registry.run_checks(graph, RunnerFilter(checks=[check_id]), None)
        return self.create_report_from_graph_checks_results(checks_results, policy['metadata'])

    def get_checks_registry(self):
        registry = Registry(parser=GraphCheckParser(), checks_dir=self.real_graph_checks_path)
        registry.load_checks()
        if self.checks_dir:
            registry.load_external_checks(self.checks_dir)
        return registry

    @abstractmethod
    def create_report_from_graph_checks_results(self, checks_results, check):
        pass

    @abstractmethod
    def assert_evaluated_keys(self, checks_results, check):
        pass


def load_yaml_data(source_file_name: str | Path, dir_path: str | Path) -> Any:
    expected_path = os.path.join(dir_path, source_file_name)
    if not os.path.exists(expected_path):
        return None

    with open(expected_path, "r") as f:
        expected_data = yaml.safe_load(f)

    return json.loads(json.dumps(expected_data))


def get_expected_results_by_file_name(test_dir: str | Path) -> (list[str], list[str]):
    if not os.path.exists(test_dir):
        return None
    expected_fail = []
    expected_pass = []
    for root, d_names, f_names in os.walk(test_dir):
        for file in f_names:
            if file.startswith('fail'):
                expected_fail.append(file)
            elif file.startswith('pass'):
                expected_pass.append(file)
            else:
                raise NameError('yaml test files should start with eiter pass / fail')

    return (expected_fail, expected_pass)


def get_policy_results(root_folder, policy):
    check_id = policy['metadata']['id']
    graph_runner = Runner()
    report = graph_runner.run(root_folder, runner_filter=RunnerFilter(checks=[check_id]))
    return report