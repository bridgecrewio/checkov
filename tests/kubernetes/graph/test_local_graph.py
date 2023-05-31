import os

from checkov.kubernetes.graph_builder.graph_components.edge_builders.ServiceAccountEdgeBuilder import \
    ServiceAccountEdgeBuilder
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.parser.parser import parse
from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_graph_flags import K8sGraphFlags
from checkov.kubernetes.kubernetes_utils import PARENT_RESOURCE_KEY_NAME, PARENT_RESOURCE_ID_KEY_NAME
from checkov.kubernetes.graph_builder.graph_components.edge_builders.LabelSelectorEdgeBuilder import LabelSelectorEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.edge_builders.KeywordEdgeBuilder import KeywordEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.edge_builders.NetworkPolicyEdgeBuilder import NetworkPolicyEdgeBuilder

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
        assert local_graph.vertices[0].id == 'Deployment.default.deployment_name'
        assert local_graph.vertices[0].attributes.get('spec').get('template') is None
        assert local_graph.vertices[0].metadata.name == 'deployment_name'
        assert local_graph.vertices[0].metadata.selector.match_labels.get('app') == 'myapp'
        assert local_graph.vertices[0].metadata.labels is None
        assert local_graph.vertices[1].id == 'Pod.default.deployment_name.app-myapp'
        assert local_graph.vertices[1].config[PARENT_RESOURCE_KEY_NAME] == 'deployment_name'
        assert local_graph.vertices[1].config[PARENT_RESOURCE_ID_KEY_NAME] == 'Deployment.default.deployment_name'
        assert local_graph.vertices[1].config.get('kind') == 'Pod'
        assert local_graph.vertices[1].config.get('apiVersion') == local_graph.vertices[0].config.get('apiVersion')
        assert len(local_graph.vertices[1].attributes.get('spec').get('containers')) == 1
        assert local_graph.vertices[1].metadata.name is None
        assert local_graph.vertices[1].metadata.selector.match_labels is None
        assert local_graph.vertices[1].metadata.labels.get('app') == 'myapp'

    def test_LabelSelectorEdgeBuilder_on_template_with_matched_label_and_selector(self) -> None:
        relative_file_path = "resources/LabelSelector/label_selector_match.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [LabelSelectorEdgeBuilder, ]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        self.assertEqual(1, len(local_graph.edges))

    def test_LabelSelectorEdgeBuilder_on_template_with_non_matched_label_and_selector(self) -> None:
        relative_file_path = "resources/LabelSelector/label_selector_non_match.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [LabelSelectorEdgeBuilder, ]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        self.assertEqual(0, len(local_graph.edges))

    def test_LabelSelectorEdgeBuilder_on_template_with_matched_and_non_matched_label_and_selector(self) -> None:
        relative_file_path = "resources/LabelSelector/label_selector_multiple_resources.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [LabelSelectorEdgeBuilder, ]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(3, len(local_graph.vertices))
        self.assertEqual(1, len(local_graph.edges))

    def test_KeywordEdgeBuilder_on_templates_with_matched_cluster_role_binding(self) -> None:
        relative_file_path = "resources/Keyword/clusterrolebinding.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [KeywordEdgeBuilder, ]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(6, len(local_graph.vertices))
        self.assertEqual(3, len(local_graph.edges))
        self.assertEqual(local_graph.edges[0].origin, 0)
        self.assertEqual(local_graph.edges[0].dest, 3)
        self.assertEqual(local_graph.edges[1].origin, 0)
        self.assertEqual(local_graph.edges[1].dest, 4)

    def test_KeywordEdgeBuilder_and_ServiceAccountEdgeBuilder_on_templates_with_pod_and_service_account(self) -> None:
        relative_file_path = "resources/Keyword/pod_service_account.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [KeywordEdgeBuilder, ServiceAccountEdgeBuilder()]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(4, len(local_graph.vertices))
        self.assertEqual(3, len(local_graph.edges))
        self.assertEqual(local_graph.edges[0].origin, 1)
        self.assertEqual(local_graph.edges[0].dest, 2)
        self.assertEqual(local_graph.edges[1].origin, 1)
        self.assertEqual(local_graph.edges[1].dest, 3)
        self.assertEqual(local_graph.edges[2].origin, 3)
        self.assertEqual(local_graph.edges[2].dest, 0)

    def test_LabelSelectorEdgeBuilder_on_templates_with_network_policy(self) -> None:
        relative_file_path = "resources/Keyword/network-policy-attached.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [NetworkPolicyEdgeBuilder, LabelSelectorEdgeBuilder]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(5, len(local_graph.vertices))
        self.assertEqual(4, len(local_graph.edges))

    def test_extracting_pod_from_container_types(self) -> None:
        relative_file_path = "resources/statefulstate_nested_resource.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [NetworkPolicyEdgeBuilder, LabelSelectorEdgeBuilder]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        self.assertEqual(1, len(local_graph.edges))

    def test_deployment_with_incompatible_selector(self) -> None:
        relative_file_path = "resources/faulty_resources/incompatible_selector.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [NetworkPolicyEdgeBuilder, LabelSelectorEdgeBuilder]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(2, len(local_graph.vertices))
        self.assertEqual(0, len(local_graph.edges))

    def test_KeywordEdgeBuilder_incompatible_cluster_role_binding(self) -> None:
        relative_file_path = "resources/faulty_resources/incompatible_clusterrolebinding.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [KeywordEdgeBuilder, ]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(6, len(local_graph.vertices))
        self.assertEqual(1, len(local_graph.edges))

    def test_deployment_with_missing_metadata(self) -> None:
        relative_file_path = "resources/faulty_resources/deployment_missing_metadata.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [NetworkPolicyEdgeBuilder, LabelSelectorEdgeBuilder]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(0, len(local_graph.vertices))
        self.assertEqual(0, len(local_graph.edges))

    def test_custom_resource_should_not_extract_pod(self) -> None:
        relative_file_path = "resources/custom_resource.yaml"
        definitions = {}
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        graph_flags = K8sGraphFlags(create_complex_vertices=True, create_edges=True)

        local_graph = KubernetesLocalGraph(definitions)
        local_graph.edge_builders = [NetworkPolicyEdgeBuilder, LabelSelectorEdgeBuilder]
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        self.assertEqual(1, len(local_graph.vertices))
        self.assertEqual(0, len(local_graph.edges))
