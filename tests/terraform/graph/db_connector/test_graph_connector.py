import os
from unittest import TestCase

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.parser import Parser

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestGraphConnector(TestCase):
    def test_creating_networkx_graph(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/encryption'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, 'AWS')
        local_graph = TerraformLocalGraph(module)
        local_graph._create_vertices()
        nxc = NetworkxConnector()
        nxc.save_graph(local_graph)

    def test_creating_igraph_graph(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/encryption'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, 'AWS')
        local_graph = TerraformLocalGraph(module)
        local_graph._create_vertices()
        igc = IgraphConnector()
        igc.save_graph(local_graph)
