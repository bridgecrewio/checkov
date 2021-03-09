import json
import os
import unittest
import warnings

import yaml
from checkov.graph.terraform import checks


class TestYamlPolicies(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['UNIQUE_TAG'] = ''
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def test_vpc_flow_log(self):
        self.go("VPCHasFlowLog")

    @staticmethod
    def go(dir_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                f"resources/{dir_name}")
        assert os.path.exists(dir_path)
        policy_dir_path = os.path.dirname(checks.__file__)
        assert os.path.exists(policy_dir_path)
        found = False
        for root, d_names, f_names in os.walk(policy_dir_path):
            for f_name in f_names:
                if f_name == f"{dir_name}.yaml":
                    found = True
                    policy = load_yaml_data(f_name, root)
                    assert policy is not None
                    expected = load_yaml_data("expected.yaml", dir_path)
                    assert expected is not None
        assert found


def load_yaml_data(source_file_name, dir_path):
    expected_path = os.path.join(dir_path, source_file_name)
    if not os.path.exists(expected_path):
        return None

    with open(expected_path, "r") as f:
        expected_data = yaml.safe_load(f)

    return json.loads(json.dumps(expected_data))
