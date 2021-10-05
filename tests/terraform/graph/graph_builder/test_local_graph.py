import os
from unittest import TestCase

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import EncryptionValues, EncryptionTypes
from checkov.common.graph.graph_builder.utils import calculate_hash
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.parser import Parser
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_manager import TerraformGraphManager

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestLocalGraph(TestCase):

    def setUp(self) -> None:
        self.source = "TERRAFORM"

    def test_update_vertices_configs_attribute_like_resource_name(self):
        config = {"resource_type": {"resource_name": {"attribute1": 1, "attribute2": 2, "resource_name": ["caution!"]}}}
        attributes = {"attribute1": 1, "attribute2": 2, "resource_name": "ok"}
        local_graph = TerraformLocalGraph(None, {})
        vertex = TerraformBlock(name="resource_type.resource_name", config=config, path='', block_type=BlockType.RESOURCE, attributes=attributes)
        vertex.changed_attributes["resource_name"] = ""
        local_graph.vertices.append(vertex)
        local_graph.update_vertices_configs()
        expected_config = {"resource_type": {"resource_name": {"attribute1": 1, "attribute2": 2, "resource_name": ["ok"]}}}
        self.assertDictEqual(expected_config, vertex.config)

    def test_single_edge_with_same_label(self):
        resources_dir = os.path.realpath(
            os.path.join(TEST_DIRNAME, '../resources/k8_service'))

        graph_manager = TerraformGraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir,
                                                                          render_variables=True)
        edges_hash = []
        for e in local_graph.edges:
            edge_hash = calculate_hash({"origin": e.origin, "dest": e.dest, "label": e.label})
            if edge_hash in edges_hash:
                origin = local_graph.vertices[e.origin]
                dest = local_graph.vertices[e.dest]
                self.fail(f'edge {e} == [{origin} - {e.label} -> {dest}] appears more than once in the graph')
            else:
                edges_hash.append(edge_hash)

    def test_set_variables_values_from_modules(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_from_module_vpc'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, tf_definitions = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                                           source=self.source)
        local_graph = TerraformLocalGraph(module, module_dependency_map)
        local_graph._create_vertices()

        variables_before_module_definitions = {
            "cidr": "0.0.0.0/0",
            "private_subnets": [],
            "public_subnets": [],
            "enable_nat_gateway": False,
            "single_nat_gateway": False,
            "enable_dns_hostnames": False,
            "public_subnet_tags": {},
            "private_subnet_tags": {},
        }

        for var_name, var_value in variables_before_module_definitions.items():
            vertex_index = local_graph.vertices_block_name_map[BlockType.VARIABLE].get(var_name)[0]
            vertex = local_graph.vertices[vertex_index]
            default_val = vertex.attributes['default']
            if type(default_val) == list:
                self.assertEqual(var_value, default_val[0])
            else:
                self.assertEqual(var_value, default_val)

        local_graph.build_graph(resources_dir)

        expected_variables_after = {
            "cidr": "172.16.0.0/16",
            "private_subnets": ["172.16.1.0/24", "172.16.2.0/24", "172.16.3.0/24"],
            "public_subnets": ["172.16.4.0/24", "172.16.5.0/24", "172.16.6.0/24"],
            "enable_nat_gateway": True,
            "single_nat_gateway": True,
            "enable_dns_hostnames": True,
            "public_subnet_tags": {"kubernetes.io/cluster/${local.cluster_name}": "shared",
                                    "kubernetes.io/role/elb": "1"},
            "private_subnet_tags": {"kubernetes.io/cluster/${local.cluster_name}" : "shared",
                                    "kubernetes.io/role/internal-elb": "1"}
        }

        for var_name, var_value in expected_variables_after.items():
            vertex_index = local_graph.vertices_block_name_map[BlockType.VARIABLE].get(var_name)[0]
            vertex = local_graph.vertices[vertex_index]
            default_val = vertex.attributes['default']
            if type(default_val) == list:
                self.assertEqual(var_value, default_val[0])
            else:
                self.assertEqual(var_value, default_val)

    def test_encryption_aws(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/encryption'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, _ = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                              self.source)
        local_graph = TerraformLocalGraph(module, module_dependency_map)
        local_graph._create_vertices()
        local_graph.calculate_encryption_attribute()
        all_attributes = [vertex.get_attribute_dict() for vertex in local_graph.vertices]
        for attribute_dict in all_attributes:
            [resource_type, resource_name] = attribute_dict[CustomAttributes.ID].split(".")
            if resource_type in ENCRYPTION_BY_RESOURCE_TYPE:
                is_encrypted = attribute_dict[CustomAttributes.ENCRYPTION]
                details = attribute_dict[CustomAttributes.ENCRYPTION_DETAILS]
                self.assertEqual(is_encrypted, EncryptionValues.ENCRYPTED.value if resource_name.startswith("encrypted")
                                 else EncryptionValues.UNENCRYPTED.value, f'failed for "{resource_type}.{resource_name}"')
                if is_encrypted == EncryptionValues.ENCRYPTED.value:
                    if 'kms_key_id' in attribute_dict or 'kms_master_key_id' in attribute_dict:
                        self.assertEqual(details, EncryptionTypes.KMS_VALUE.value, f'Bad encryption details for "{resource_type}.{resource_name}"')
                    else:
                        self.assertIn(details, [EncryptionTypes.AES256.value, EncryptionTypes.KMS_VALUE.value, EncryptionTypes.NODE_TO_NODE.value, EncryptionTypes.DEFAULT_KMS.value], f'Bad encryption details for "{resource_type}.{resource_name}"')
                else:
                    self.assertEqual(details, "")
            else:
                self.assertIsNone(attribute_dict.get(CustomAttributes.ENCRYPTION))
                self.assertIsNone(attribute_dict.get(CustomAttributes.ENCRYPTION_DETAILS))

    def test_vertices_from_local_graph(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_from_module_vpc'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, _ = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                              self.source)
        local_graph = TerraformLocalGraph(module, module_dependency_map)
        local_graph._create_vertices()
        tf_definitions, breadcrumbs = convert_graph_vertices_to_tf_definitions(local_graph.vertices, resources_dir)
        self.assertIsNotNone(tf_definitions)
        self.assertIsNotNone(breadcrumbs)

    def test_module_dependencies(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/stacks'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        self.assertEqual(module_dependency_map[f'{resources_dir}/prod'], [[]])
        self.assertEqual(module_dependency_map[f'{resources_dir}/stage'], [[]])
        self.assertEqual(module_dependency_map[f'{resources_dir}/test'], [[]])
        self.assertEqual(module_dependency_map[f'{resources_dir}/prod/sub-prod'], [[f'{resources_dir}/prod/main.tf']])
        expected_inner_modules = [
            [f'{resources_dir}/prod/main.tf', f'{resources_dir}/prod/sub-prod/main.tf'],
            [f'{resources_dir}/stage/main.tf'],
            [f'{resources_dir}/test/main.tf']
        ]
        self.assertEqual(module_dependency_map[f'{os.path.dirname(resources_dir)}/s3_inner_modules'], expected_inner_modules)
        self.assertEqual(module_dependency_map[f'{os.path.dirname(resources_dir)}/s3_inner_modules/inner'],
                         list(map(lambda dep_list: dep_list + [f'{os.path.dirname(resources_dir)}/s3_inner_modules/main.tf'],
                                  expected_inner_modules)))

    def test_blocks_from_local_graph_module(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/stacks'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, _ = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                              self.source)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.RESOURCE and block.name == 'aws_s3_bucket.inner_s3', module.blocks))), 3)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.MODULE and block.name == 'inner_module_call', module.blocks))), 3)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.MODULE and block.name == 's3', module.blocks))), 3)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.MODULE and block.name == 'sub-module', module.blocks))), 1)

    def test_vertices_from_local_graph_module(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/stacks'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, _ = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                              self.source)
        local_graph = TerraformLocalGraph(module, module_dependency_map)
        local_graph.build_graph(render_variables=True)

        self.assertEqual(12, len(local_graph.edges))

    def test_variables_same_name_different_modules(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/same_var_names'))
        hcl_config_parser = Parser()
        module, module_dependency_map, _, _ = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                              self.source)
        local_graph = TerraformLocalGraph(module, module_dependency_map)
        local_graph.build_graph(render_variables=True)
        print(local_graph.edges)
        self.assertEqual(12, len(local_graph.edges))
        self.assertEqual(13, len(local_graph.vertices))

        module_variable_edges = [
            e for e in local_graph.edges
            if local_graph.vertices[e.dest].block_type == "module" and local_graph.vertices[e.dest].path.endswith(
                'same_var_names/module2/main.tf')
        ]

        # Check they point to 2 different modules
        self.assertEqual(2, len(module_variable_edges))
        self.assertNotEqual(local_graph.vertices[module_variable_edges[0].origin],
                            local_graph.vertices[module_variable_edges[1].origin])


        module_variable_edges = [
            e for e in local_graph.edges
            if local_graph.vertices[e.dest].block_type == "module" and local_graph.vertices[e.dest].path.endswith('same_var_names/module1/main.tf')
        ]

        # Check they point to 2 different modules
        self.assertEqual(2, len(module_variable_edges))
        self.assertNotEqual(local_graph.vertices[module_variable_edges[0].origin], local_graph.vertices[module_variable_edges[1].origin])
