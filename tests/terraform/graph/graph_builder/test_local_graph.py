import os
from pathlib import Path
from unittest import TestCase

import mock
import json

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import EncryptionValues, EncryptionTypes
from checkov.common.graph.graph_builder.utils import calculate_hash
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.util.parser_utils import TERRAFORM_NESTED_MODULE_PATH_PREFIX, TERRAFORM_NESTED_MODULE_PATH_ENDING, \
    TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.graph_to_tf_definitions import convert_graph_vertices_to_tf_definitions
from checkov.terraform.parser import Parser
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform.tf_parser import TFParser
from checkov.terraform.modules.module_utils import clean_parser_types, serialize_definitions

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestLocalGraph(TestCase):
    def setUp(self) -> None:
        self.source = "TERRAFORM"

    def test_update_vertices_configs_attribute_like_resource_name(self):
        config = {"resource_type": {"resource_name": {"attribute1": 1, "attribute2": 2, "resource_name": ["caution!"]}}}
        attributes = {"attribute1": 1, "attribute2": 2, "resource_name": "ok"}
        local_graph = TerraformLocalGraph(None)
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

    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    def test_set_variables_values_from_modules(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_from_module_vpc'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, source=self.source)
        local_graph = TerraformLocalGraph(module)
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
            "private_subnet_tags": {"kubernetes.io/cluster/${local.cluster_name}": "shared",
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

    def test_definition_creation_by_dirs(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_local_from_variable'))
        hcl_config_parser = TFParser()
        tf_definitions = hcl_config_parser.parse_directory(directory=resources_dir)
        tf_definitions = clean_parser_types(tf_definitions)
        tf_definitions = serialize_definitions(tf_definitions)

        dirs_to_definitions = hcl_config_parser.create_definition_by_dirs(tf_definitions)
        assert len(dirs_to_definitions) == 1
        single_dir_element = list(dirs_to_definitions.values())[0]
        assert list(single_dir_element[0].values()) == [{'locals': [{'__end_line__': 3, '__start_line__': 1, 'bucket_name': ['${var.var_bucket_name}']}]}]
        assert list(single_dir_element[1].values()) == [{'variable': [{'var_bucket_name': {'__end_line__': 3, '__start_line__': 1, 'default': ['test_bucket_name']}}]}]

    def test_definition_creation_by_dirs_multi_nodule(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/modules/linked_modules'))
        hcl_config_parser = TFParser()
        tf_definitions = hcl_config_parser.parse_directory(directory=resources_dir)
        tf_definitions = clean_parser_types(tf_definitions)
        tf_definitions = serialize_definitions(tf_definitions)

        dirs_to_definitions = hcl_config_parser.create_definition_by_dirs(tf_definitions)
        assert len(dirs_to_definitions) == 2
        lambda_element = list(dirs_to_definitions.values())[0]
        s3_bucket_element = list(dirs_to_definitions.values())[1]
        assert len(lambda_element) + len(s3_bucket_element) == len(tf_definitions)
        modules = hcl_config_parser.parse_multi_graph_hcl_module(resources_dir, source=self.source)
        assert len(modules) == 2
        assert 'lambda' in modules[0][0].source_dir
        assert 's3-bucket' in modules[1][0].source_dir


    def test_compare_multi_graph_defs(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_module_postgresql'))
        hcl_config_parser = TFParser()
        module, defs = hcl_config_parser.parse_hcl_module(resources_dir, source=self.source)
        modules = hcl_config_parser.parse_multi_graph_hcl_module(resources_dir, source=self.source)
        for idx, module_to_definitions in enumerate(modules):
            assert module_to_definitions[0] == module
            for att, content in defs.items():
                found = False
                for content_dict in module_to_definitions[1]:
                    for key, value in content_dict.items():
                        if value == content:
                            found = True
                            break
                    if found:
                        break
                assert found

    def test_set_variables_values_from_modules_with_new_tf_parser(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_from_module_vpc'))
        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, source=self.source)
        local_graph = TerraformLocalGraph(module)
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
            "private_subnet_tags": {"kubernetes.io/cluster/${local.cluster_name}": "shared",
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
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph._create_vertices()
        local_graph.calculate_encryption_attribute(ENCRYPTION_BY_RESOURCE_TYPE)
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
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph._create_vertices()
        tf_definitions, breadcrumbs = convert_graph_vertices_to_tf_definitions(local_graph.vertices, resources_dir)
        self.assertIsNotNone(tf_definitions)
        self.assertIsNotNone(breadcrumbs)

    def test_module_dependencies(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/stacks'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        self.assertEqual(module.module_dependency_map[f'{resources_dir}/prod'], [[]])
        self.assertEqual(module.module_dependency_map[f'{resources_dir}/stage'], [[]])
        self.assertEqual(module.module_dependency_map[f'{resources_dir}/test'], [[]])
        self.assertEqual(module.module_dependency_map[f'{resources_dir}/prod/sub-prod'], [[f'{resources_dir}/prod/main.tf']])
        expected_inner_modules = [
            [
                f'{resources_dir}/prod/main.tf',
                f'{resources_dir}/prod/sub-prod/main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{resources_dir}/prod/main.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}',
            ],
            [
                f'{resources_dir}/stage/main.tf'
            ],
            [
                f'{resources_dir}/test/main.tf'
            ],
        ]
        self.assertEqual(module.module_dependency_map[f'{os.path.dirname(resources_dir)}/s3_inner_modules'], expected_inner_modules)
        resources_dir_no_stacks = resources_dir.replace('/stacks', '')
        expected_inner_modules = [
            [
                f'{resources_dir}/prod/main.tf',
                f'{resources_dir}/prod/sub-prod/main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{resources_dir}/prod/main.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}',
                f'{resources_dir_no_stacks}/s3_inner_modules/main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{resources_dir}/prod/sub-prod/main.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{resources_dir}/prod/main.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}{TERRAFORM_NESTED_MODULE_PATH_ENDING}',
            ],
            [
                f'{resources_dir}/stage/main.tf',
                f'{resources_dir_no_stacks}/s3_inner_modules/main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{resources_dir}/stage/main.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}',
            ],
            [
                f'{resources_dir}/test/main.tf',
                f'{resources_dir_no_stacks}/s3_inner_modules/main.tf{TERRAFORM_NESTED_MODULE_PATH_PREFIX}{resources_dir}/test/main.tf{TERRAFORM_NESTED_MODULE_INDEX_SEPARATOR}0{TERRAFORM_NESTED_MODULE_PATH_ENDING}',
            ],
        ]
        self.assertEqual(module.module_dependency_map[f'{os.path.dirname(resources_dir)}/s3_inner_modules/inner'], expected_inner_modules)

    def test_blocks_from_local_graph_module(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/stacks'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.RESOURCE and block.name == 'aws_s3_bucket.inner_s3', module.blocks))), 3)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.MODULE and block.name == 'inner_module_call', module.blocks))), 3)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.MODULE and block.name == 's3', module.blocks))), 3)
        self.assertEqual(len(list(filter(lambda block: block.block_type == BlockType.MODULE and block.name == 'sub-module', module.blocks))), 1)

    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    def test_vertices_from_local_graph_module(self):
        parent_dir = Path(TEST_DIRNAME).parent
        resources_dir = str(parent_dir / "resources/modules/stacks")
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(render_variables=True)

        self.assertEqual(12, len(local_graph.edges))

        # check vertex breadcrumbs
        bucket_vertex_1 = next(
            vertex
            for vertex in local_graph.vertices
            if vertex.name == "aws_s3_bucket.inner_s3" and vertex.source_module == {6}
        )
        bucket_vertex_2 = next(
            vertex
            for vertex in local_graph.vertices
            if vertex.name == "aws_s3_bucket.inner_s3" and vertex.source_module == {7}
        )
        bucket_vertex_3 = next(
            vertex
            for vertex in local_graph.vertices
            if vertex.name == "aws_s3_bucket.inner_s3" and vertex.source_module == {8}
        )
        self.assertDictEqual(
            {
                "versioning.enabled": [
                    {
                        "type": "module",
                        "name": "inner_module_call",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/main.tf"),
                        "module_connection": False,
                    },
                    {
                        "type": "variable",
                        "name": "versioning",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/inner/variables.tf"),
                        "module_connection": False,
                    },
                ],
                "source_module_": [
                    {
                        "type": "module",
                        "name": "sub-module",
                        "path": str(parent_dir / "resources/modules/stacks/prod/main.tf"),
                        "idx": 12
                    },
                    {
                        "type": "module",
                        "name": "s3",
                        "path": str(parent_dir / "resources/modules/stacks/prod/sub-prod/main.tf"),
                        "idx": 13
                    },
                    {
                        "type": "module",
                        "name": "inner_module_call",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/main.tf"),
                        "idx": 6
                    },
                ],
            },
            bucket_vertex_1.breadcrumbs,
        )

        self.assertDictEqual(
            {
                "versioning.enabled": [
                    {
                        "type": "module",
                        "name": "inner_module_call",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/main.tf"),
                        "module_connection": False,
                    },
                    {
                        "type": "variable",
                        "name": "versioning",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/inner/variables.tf"),
                        "module_connection": False,
                    },
                ],
                "source_module_": [
                    {
                        "type": "module",
                        "name": "s3",
                        "path": str(parent_dir / "resources/modules/stacks/stage/main.tf"),
                        "idx": 14
                    },
                    {
                        "type": "module",
                        "name": "inner_module_call",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/main.tf"),
                        "idx": 7
                    },
                ],
            },
            bucket_vertex_2.breadcrumbs,
        )

        self.assertDictEqual(
            {
                "versioning.enabled": [
                    {
                        "type": "module",
                        "name": "inner_module_call",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/main.tf"),
                        "module_connection": False,
                    },
                    {
                        "type": "variable",
                        "name": "versioning",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/inner/variables.tf"),
                        "module_connection": False,
                    },
                ],
                "source_module_": [
                    {
                        "type": "module",
                        "name": "s3",
                        "path": str(parent_dir / "resources/modules/stacks/test/main.tf"),
                        "idx": 15
                    },
                    {
                        "type": "module",
                        "name": "inner_module_call",
                        "path": str(parent_dir / "resources/modules/s3_inner_modules/main.tf"),
                        "idx": 8
                    },
                ],
            },
            bucket_vertex_3.breadcrumbs,
        )

    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    def test_variables_same_name_different_modules(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/same_var_names'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
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

    def test_variables_same_name_different_modules_with_new_tf_parser(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/same_var_names'))
        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
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

    def test_variables_same_name_different_modules_with_new_tf_parser(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/same_var_names'))
        hcl_config_parser = TFParser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
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

    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    def test_nested_modules_instances(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/nested_modules_instances'))
        hcl_config_parser = Parser()
        module, _ = hcl_config_parser.parse_hcl_module(resources_dir, self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(render_variables=True)

        vertices = [vertex.to_dict() for vertex in local_graph.vertices]
        edges = [edge.to_dict() for edge in local_graph.edges]

        with open(os.path.realpath(os.path.join(TEST_DIRNAME, '../resources/modules/nested_modules_instances/expected_local_graph.json')), 'r') as f:
            expected = json.load(f)

        self.assertCountEqual(
            json.loads(json.dumps(vertices).replace(resources_dir, '')),
            json.loads(json.dumps(expected.get('vertices')).replace(resources_dir, '')),

        )
        self.assertCountEqual(edges, expected.get('edges'))
