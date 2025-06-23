import os
from pathlib import Path


from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_utils import build_resource_id_from_labels, PARENT_RESOURCE_KEY_NAME, get_folder_definitions

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = os.path.join("resources", "definitions")
FILE_UNDER_HIDDEN_FOLDER = '/home/runner/work/checkov/checkov/tests/kubernetes/graph/resources/definitions/.hidden/graph_check.yaml'
FILE_NOT_HIDDEN = '/home/runner/work/checkov/checkov/tests/kubernetes/graph/resources/definitions/custom_resource.yaml'


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
        os.environ["IGNORE_HIDDEN_DIRECTORY_ENV"] = "False"
        test_root_dir = Path(TEST_DIRNAME) / RELATIVE_PATH
        definitions, _ = get_folder_definitions(root_folder=test_root_dir, excluded_paths=[])
        file_list = list(definitions.keys())
        
        self.assertIn(FILE_UNDER_HIDDEN_FOLDER, file_list)
        self.assertIn(FILE_NOT_HIDDEN, file_list)
    
    def test_get_folder_definitions_without_hidden(self) -> None:
        test_root_dir = Path(TEST_DIRNAME) / RELATIVE_PATH
        definitions, _ = get_folder_definitions(test_root_dir, [])
        file_list = list(definitions.keys())

        self.assertNotIn(FILE_UNDER_HIDDEN_FOLDER, file_list)
        self.assertIn(FILE_NOT_HIDDEN, file_list)
