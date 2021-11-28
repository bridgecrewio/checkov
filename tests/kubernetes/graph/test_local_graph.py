import os

from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.parser.parser import parse
from tests.kubernetes.graph.base_graph_tests import TestGraph

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestKubernetesLocalGraph(TestGraph):
    def test_build_graph_with_single_resource(self):
        relative_file_path = "../checks/example_AllowedCapabilities/cronjob-PASSED.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        resource = definitions[relative_file_path][0]

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        self.assertEqual(1, len(local_graph.vertices))
        self.assert_vertex(local_graph.vertices[0], resource)

    def test_build_graph_with_multi_resources(self):
        relative_file_path = "../checks/example_DefaultNamespace/default-k8s-service-and-sa-PASSED2.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False)
        self.assertEqual(4, len(local_graph.vertices))
