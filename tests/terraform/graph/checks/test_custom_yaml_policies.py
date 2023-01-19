from __future__ import annotations

import json
import os
import unittest
import warnings
from pathlib import Path
from typing import Any

import yaml

from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform import checks
from checkov.terraform.runner import Runner


class TestCustomYamlPolicies(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_CustomPolicy1(self):
        self.go("CustomPolicy1")

    def go(self, dir_name: str, check_name: str | None = None) -> None:
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"resources/{dir_name}")
        check_name = dir_name if check_name is None else check_name
        assert os.path.exists(dir_path)
        policy_dir_path = str(Path(__file__).parent / "custom_policies")
        assert os.path.exists(policy_dir_path)
        found = False
        for root, d_names, f_names in os.walk(policy_dir_path):
            for f_name in f_names:
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

    def assert_entities(self, expected_entities: list[str], results: list[CheckResult], assertion: bool) -> None:
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


def get_policy_results(root_folder, policy):
    check_id = policy['metadata']['id']
    graph_runner = Runner()
    report = graph_runner.run(root_folder, runner_filter=RunnerFilter(checks=[check_id]))
    return report


def wrap_policy(policy):
    policy['query'] = policy['definition']
    del policy['definition']


def load_yaml_data(source_file_name: str, dir_path: str) -> dict[str, Any] | None:
    expected_path = os.path.join(dir_path, source_file_name)
    if not os.path.exists(expected_path):
        return None

    with open(expected_path, "r") as f:
        expected_data = yaml.safe_load(f)

    return json.loads(json.dumps(expected_data))

    def test_Route53ZoneEnableDNSSECSigning(self):
        self.go("Route53ZoneEnableDNSSECSigning")

    def test_Route53ZoneHasMatchingQueryLog(self):
        self.go("Route53ZoneHasMatchingQueryLog")