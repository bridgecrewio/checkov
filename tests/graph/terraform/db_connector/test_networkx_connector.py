import copy
import os
from unittest import TestCase

from checkov.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.graph.terraform.graph_builder.local_graph import LocalGraph
from checkov.graph.terraform.parser import TerraformGraphParser

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestNetworkxConnector(TestCase):
    def test_creating_graph(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/encryption'))
        hcl_config_parser = TerraformGraphParser()
        module, module_dependency_map, _ = hcl_config_parser.parse_hcl_module(resources_dir, 'AWS')
        local_graph = LocalGraph(module, module_dependency_map)
        local_graph._create_vertices()
        nxc = NetworkxConnector()
        nxc.save_graph(local_graph)

    def test_get_vertices(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/encryption'))
        hcl_config_parser = TerraformGraphParser()
        module, module_dependency_map, _ = hcl_config_parser.parse_hcl_module(resources_dir, 'AWS')
        local_graph = LocalGraph(module, module_dependency_map)
        local_graph._create_vertices()
        nxc = NetworkxConnector()
        nxc.save_graph(local_graph)

        vertices = nxc.get_vertices_attributes()
        original_vertices = copy.deepcopy(local_graph.vertices)
        for v in vertices:
            try:
                matched_v = next(v_source for v_source in original_vertices if v_source.path == v[CustomAttributes.FILE_PATH] and v_source.name == v[CustomAttributes.BLOCK_NAME])
                original_vertices.remove(matched_v)
            except Exception:
                self.fail(f"Did not find a match for node {v}")

        self.assertEqual(len(original_vertices), 0)

