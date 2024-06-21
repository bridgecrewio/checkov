import unittest
from pathlib import Path

from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.tf_parser import TFParser


class TestModuleProvider(unittest.TestCase):
    def test_module_with_two_providers(self):
        test_files_dir = Path(__file__).parent / "example_ModuleProvider"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        assert len(local_graph.edges) == 2
        assert local_graph.vertices[0].attributes.get('__provider_address__') == local_graph.vertices[3].attributes.get('__address__')
        assert local_graph.vertices[0].attributes.get('__provider_address__') == local_graph.vertices[3].config['aws'].get('__address__')
        assert local_graph.edges[0].origin == 1 and local_graph.edges[0].dest == 3
        assert local_graph.edges[1].origin == 0 and local_graph.edges[1].dest == 3

    def test_module_with_one_def_provider(self):
        test_files_dir = Path(__file__).parent / "example_module_with_one_provider"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        resource_provider_address = local_graph.vertices[0].attributes.get('__provider_address__')
        default_provider_address_from_module = local_graph.vertices[2].attributes.get('__address__')

        assert resource_provider_address == default_provider_address_from_module

    def test_resource_with_def_provider(self):
        test_files_dir = Path(__file__).parent / "example_provider_without_module"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        # assert resource with provider ref.
        resource_provider_address_with_alias = local_graph.vertices[2].attributes.get('__provider_address__')
        provider_address_with_alias = local_graph.vertices[1].attributes.get('__address__')
        assert resource_provider_address_with_alias == provider_address_with_alias

        # assert resource without ref to the default provider
        resource_provider_address_default = local_graph.vertices[3].attributes.get('__provider_address__')
        provider_address_default = local_graph.vertices[0].attributes.get('__address__')
        assert resource_provider_address_default == provider_address_default

    def test_provider_nested_module(self):
        test_files_dir = Path(__file__).parent / "example_provider_with_nested_module"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        # assert resource with provider ref.
        resource_provider_address_with_alias = local_graph.vertices[2].attributes.get('__provider_address__')
        provider_address_with_alias = local_graph.vertices[1].attributes.get('__address__')
        assert resource_provider_address_with_alias == provider_address_with_alias

    def test_example_provider_with_nested_module_assign_provider(self):
        test_files_dir = Path(__file__).parent / "example_provider_with_nested_module_assign_provider"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        # assert resource with provider ref.
        resource_provider_address_with_alias = local_graph.vertices[0].attributes.get('__provider_address__')
        provider_address_with_alias = local_graph.vertices[4].attributes.get('__address__')
        assert resource_provider_address_with_alias == provider_address_with_alias

    def test_provider_edge_cases(self):
        test_files_dir = Path(__file__).parent / "example_provider_edge_case"

        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(test_files_dir, source='TERRAFORM')
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(True)

        assert local_graph.vertices[3].attributes.get('__provider_address__') == "aws.default"
        assert local_graph.vertices[8].attributes.get('__provider_address__') == "module.level1.aws.default"
        assert local_graph.vertices[9].attributes.get('__provider_address__') == "module.level1.aws.default"
        assert local_graph.vertices[10].attributes.get('__provider_address__') == "module.level1.aws.eu_west"
        assert local_graph.vertices[11].attributes.get('__provider_address__') == "aws.default"


if __name__ == "__main__":
    unittest.main()
