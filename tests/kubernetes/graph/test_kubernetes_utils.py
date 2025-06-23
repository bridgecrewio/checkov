import os
from pathlib import Path


from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_utils import build_resource_id_from_labels, PARENT_RESOURCE_KEY_NAME, get_folder_definitions

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = os.path.join("resources", "definitions")


class TestKubernetesUtilsZ(TestGraph):
    def test_build_resource_id_from_labels(self) -> None:
        resource = {PARENT_RESOURCE_KEY_NAME: "deployment_name"}
        resource_type = "Pod"
        namespace = "default"
        labels = {"app": "foo", "cluster": "bar"}
        result = build_resource_id_from_labels(resource_type, namespace, labels, resource)
        self.assertEqual(result, "Pod.default.deployment_name.app-foo.cluster-bar")

    def test_build_resource_id_from_empty_labels(self) -> None:
        resource = {PARENT_RESOURCE_KEY_NAME: "deployment_name"}
        resource_type = "Pod"
        namespace = "namespace"
        labels = {}
        result = build_resource_id_from_labels(resource_type, namespace, labels, resource)
        self.assertEqual(result, "Pod.namespace.deployment_name.default")
    
    def test_get_folder_definitions_with_hidden(self) -> None:
        include_hidden = [".hidden"]
        test_root_dir = Path(TEST_DIRNAME) / RELATIVE_PATH
        definitions, definitions_raw = get_folder_definitions(root_folder=test_root_dir, excluded_paths=[], include_hidden=include_hidden)
        print(definitions)
        print(definitions_raw)
        self.assertEqual(definitions, "Pod.namespace.deployment_name.default")
        self.assertEqual(definitions_raw, "Pod.namespace.deployment_name.default")
    
    def test_get_folder_definitions_without_hidden(self) -> None:
        test_root_dir = Path(TEST_DIRNAME) / RELATIVE_PATH
        definitions, definitions_raw = get_folder_definitions(test_root_dir)
        print(definitions)
        print(definitions_raw)
        self.assertEqual(definitions, "Pod.namespace.deployment_name.default")
        self.assertEqual(definitions_raw, "Pod.namespace.deployment_name.default")
