import os

from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_utils import build_resource_id_from_labels, PARENT_RESOURCE_KEY_NAME, should_include_path

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = os.path.join("resources", "definitions")
PATH_HIDDEN = "/Users/mblonder/dev/checkov/tests/kubernetes/graph/resources/definitions/.hidden/graph_check.yaml"
PATH_NOT_HIDDEN = "/Users/mblonder/dev/checkov/tests/kubernetes/graph/resources/definitions/not_hidden/graph_check.yaml"


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
    
    def test_should_include_path_include_hidden(self) -> None:
        ignore_hidden_dir = False

        should_include_hidden = should_include_path(PATH_HIDDEN, ignore_hidden_dir)
        should_include_not_hidden = should_include_path(PATH_NOT_HIDDEN, ignore_hidden_dir)

        self.assertEqual(should_include_hidden, True)
        self.assertEqual(should_include_not_hidden, True)
    
    def test_should_include_path_not_include_hidden(self) -> None:
        ignore_hidden_dir = True

        should_include_hidden = should_include_path(PATH_HIDDEN, ignore_hidden_dir)
        should_include_not_hidden = should_include_path(PATH_NOT_HIDDEN, ignore_hidden_dir)

        self.assertEqual(should_include_hidden, False)
        self.assertEqual(should_include_not_hidden, True)


