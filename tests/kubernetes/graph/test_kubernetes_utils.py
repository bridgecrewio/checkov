import os


from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_utils import build_resource_id_from_labels

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestKubernetesUtilsZ(TestGraph):
    def test_build_resource_id_from_labels(self) -> None:
        resource_type = "Pod"
        namespace = "default"
        labels = {"app": "foo", "cluster": "bar"}
        result = build_resource_id_from_labels(resource_type, namespace, labels)
        self.assertEqual(result, "Pod.default.app-foo.cluster-bar")

    def test_build_resource_id_from_empty_labels(self) -> None:
        resource_type = "Pod"
        namespace = "namespace"
        labels = {}
        result = build_resource_id_from_labels(resource_type, namespace, labels)
        self.assertEqual(result, "Pod.namespace.default")