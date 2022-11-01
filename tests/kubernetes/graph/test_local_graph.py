import os

from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.parser.parser import parse
from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_utils import K8sGraphFlags

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestKubernetesLocalGraph(TestGraph):
    def test_build_graph_with_single_resource(self) -> None:
        relative_file_path = "../checks/example_AllowedCapabilities/cronjob-PASSED.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        resource = definitions[relative_file_path][0]

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False, graph_flags=K8sGraphFlags())
        self.assertEqual(1, len(local_graph.vertices))
        self.assert_vertex(local_graph.vertices[0], resource)

    def test_build_graph_with_multi_resources(self) -> None:
        relative_file_path = "../checks/example_DefaultNamespace/default-k8s-service-and-sa-PASSED2.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False, graph_flags=K8sGraphFlags())
        self.assertEqual(4, len(local_graph.vertices))

    def test_build_graph_with_nested_resources(self) -> None:
        file = os.path.join(TEST_DIRNAME, 'resources', 'nested_resource.yaml')
        definitions = {}
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=False)
        (definitions[file], definitions_raw) = parse(file)
        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        assert local_graph.vertices[0].id == 'Deployment.default.myapp'
        assert local_graph.vertices[0].attributes.get('spec').get('template') is None
        assert local_graph.vertices[0].metadata.name == 'myapp'
        assert local_graph.vertices[0].metadata.selector.match_labels.get('app') == 'myapp'
        assert local_graph.vertices[0].metadata.labels is None
        assert local_graph.vertices[1].id == "Pod.default.{'app': 'myapp'}"
        assert len(local_graph.vertices[1].attributes.get('spec').get('containers')) == 1
        assert local_graph.vertices[1].metadata.name is None
        assert local_graph.vertices[1].metadata.selector.match_labels is None
        assert local_graph.vertices[1].metadata.labels.get('app') == 'myapp'

    def test_graph_data_on_template_with_matched_label_and_selector(self) -> None:
        relative_file_path = "resources/LabelSelector/label_selector_match.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        self.assertEqual(1, len(local_graph.edges))

    def test_graph_data_on_template_with_non_matched_label_and_selector(self) -> None:
        relative_file_path = "resources/LabelSelector/label_selector_non_match.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        self.assertEqual(0, len(local_graph.edges))

    def test_graph_data_on_template_with_matched_and_non_matched_label_and_selector(self) -> None:
        relative_file_path = "resources/LabelSelector/label_selector_multiple_resources.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(3, len(local_graph.vertices))
        self.assertEqual(1, len(local_graph.edges))
