import unittest
from pathlib import Path

from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.tf_parser import TFParser


class TestModuleProvider(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_ModuleProvider"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        assert len(local_graph.edges) == 2
        assert local_graph.edges[0].origin == 1 and local_graph.edges[0].dest == 3
        assert local_graph.edges[1].origin == 0 and local_graph.edges[1].dest == 3

if __name__ == "__main__":
    unittest.main()
