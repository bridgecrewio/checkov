import os

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.kubernetes.graph_manager import KubernetesGraphManager
from checkov.kubernetes.parser.parser import parse
from tests.kubernetes.graph.base_graph_tests import TestGraph
from checkov.kubernetes.kubernetes_graph_flags import K8sGraphFlags

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestKubernetesGraphManager(TestGraph):
    def test_build_graph_from_source_directory_no_rendering(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, "../runner/resources"))
        graph_manager = KubernetesGraphManager(db_connector=NetworkxConnector())
        graph_flags = K8sGraphFlags(create_complex_vertices=False, create_edges=False)
        graph_manager.graph_flags = graph_flags
        local_graph, definitions = graph_manager.build_graph_from_source_directory(root_dir, render_variables=False)

        expected_resources_by_file = {
            os.path.join(root_dir, "example.yaml"): [
                "Service.default.kafka-hs"],
            os.path.join(root_dir, "example_multiple.yaml"): [
                "PodDisruptionBudget.a.a",
                "Service.default.a"],
            os.path.join(root_dir, "graph.yaml"): [
                "StatefulSet.default.cassandra",
                "Deployment.default.my-nginx",
                "Pod.default.cassandra.app-cassandra",
                "Pod.default.my-nginx.app-nginx"]
        }
        self.assertEqual(7, len(local_graph.vertices))
        self.assertEqual(7, len(local_graph.vertices_by_block_type[BlockType.RESOURCE]))

        for v in local_graph.vertices:
            self.assertIn(v.name, expected_resources_by_file[v.path])

    def test_build_graph_from_definitions(self):
        relative_file_path = "../checks/example_AllowedCapabilities/cronjob-PASSED.yaml"
        definitions = {}
        graph_flags = K8sGraphFlags(create_complex_vertices=False, create_edges=False)
        file = os.path.realpath(os.path.join(TEST_DIRNAME, relative_file_path))
        (definitions[relative_file_path], definitions_raw) = parse(file)
        resource = definitions[relative_file_path][0]

        graph_manager = KubernetesGraphManager(db_connector=NetworkxConnector())
        graph_manager.graph_flags = graph_flags
        local_graph = graph_manager.build_graph_from_definitions(definitions)
        self.assertEqual(1, len(local_graph.vertices))
        self.assert_vertex(local_graph.vertices[0], resource)
