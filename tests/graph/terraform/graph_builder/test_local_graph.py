import json
import os
from unittest import TestCase

from checkov.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.graph.graph_builder.graph_components.attribute_names import EncryptionValues, EncryptionTypes
from checkov.graph.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.graph.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.graph.terraform.graph_builder.graph_components.blocks import Block
from checkov.graph.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.graph.terraform.parser import TerraformGraphParser
from checkov.graph.terraform.graph_builder.local_graph import LocalGraph
from checkov.graph.terraform.graph_manager import GraphManager
from checkov.graph.terraform.utils.utils import calculate_hash, decode_graph_property_value

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestLocalGraph(TestCase):

    def setUp(self) -> None:
        self.source = "TERRAFORM"

    def test__attribute_has_nested_attributes_dictionary(self):
        local_graph = LocalGraph(module={}, module_dependency_map={})

        attributes = {'name': ['${var.lb_name}'], 'internal': [True], 'security_groups': ['${var.lb_security_group_ids}'], 'subnets': ['${var.subnet_id}'], 'enable_deletion_protection': [True], 'tags': {'Terraform': True, 'Environment': 'sophi-staging'}, 'resource_type': ['aws_alb'], 'tags.Terraform': True, 'tags.Environment': 'sophi-staging'}
        self.assertTrue(local_graph._attribute_has_nested_attributes(attribute_key='tags', attributes=attributes))
        self.assertFalse(local_graph._attribute_has_nested_attributes(attribute_key='name', attributes=attributes))
        self.assertFalse(local_graph._attribute_has_nested_attributes(attribute_key='tags.Environment', attributes=attributes))

    def test__attribute_has_nested_attributes_list(self):
        local_graph = LocalGraph(module={}, module_dependency_map={})

        attributes = {'most_recent': [True], 'filter': [{'name': 'name', 'values': ['amzn-ami-hvm-*-x86_64-gp2']}, {'name': 'owner-alias', 'values': ['amazon']}], 'filter.0': {'name': 'name', 'values': ['amzn-ami-hvm-*-x86_64-gp2']}, 'filter.0.name': 'name', 'filter.0.values': ['amzn-ami-hvm-*-x86_64-gp2'], 'filter.0.values.0': 'amzn-ami-hvm-*-x86_64-gp2', 'filter.1': {'name': 'owner-alias', 'values': ['amazon']}, 'filter.1.name': 'owner-alias', 'filter.1.values': ['amazon'], 'filter.1.values.0': 'amazon'}
        self.assertTrue(local_graph._attribute_has_nested_attributes(attribute_key='filter', attributes=attributes))
        self.assertTrue(local_graph._attribute_has_nested_attributes(attribute_key='filter.1.values', attributes=attributes))
        self.assertFalse(local_graph._attribute_has_nested_attributes(attribute_key='filter.1.values.0', attributes=attributes))

    def test_update_vertices_configs_attribute_like_resource_name(self):
        config = {"resource_type": {"resource_name": {"attribute1": 1, "attribute2": 2, "resource_name": ["caution!"]}}}
        attributes = {"attribute1": 1, "attribute2": 2, "resource_name": "ok"}
        local_graph = LocalGraph(None, {})
        vertex = Block(name="resource_type.resource_name", config=config, path='', block_type=BlockType.RESOURCE, attributes=attributes)
        vertex.changed_attributes["resource_name"] = ""
        local_graph.vertices.append(vertex)
        local_graph.update_vertices_configs()
        expected_config = {"resource_type": {"resource_name": {"attribute1": 1, "attribute2": 2, "resource_name": ["ok"]}}}
        self.assertDictEqual(expected_config, vertex.config)

    def test_single_edge_with_same_label(self):
        resources_dir = os.path.realpath(
            os.path.join(TEST_DIRNAME, '../resources/k8_service'))

        graph_manager = GraphManager(NetworkxConnector())
        local_graph, _ = graph_manager.build_graph_from_source_directory(resources_dir,
                                                                          render_variables=True)
        edges_hash = []
        for e in local_graph.edges:
            edge_hash = calculate_hash(e)
            if edge_hash in edges_hash:
                origin = local_graph.vertices[e.origin]
                dest = local_graph.vertices[e.dest]
                self.fail(f'edge {e} == [{origin} - {e.label} -> {dest}] appears more than once in the graph')
            else:
                edges_hash.append(edge_hash)

    def test_set_variables_values_from_modules(self):
        resources_dir = os.path.realpath(os.path.join(TEST_DIRNAME,
                                                      '../resources/variable_rendering/render_from_module_vpc'))
        hcl_config_parser = TerraformGraphParser()
        module, module_dependency_map, tf_definitions = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                                           source=self.source)
        local_graph = LocalGraph(module, module_dependency_map)
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

        local_graph._set_variables_values_from_modules()

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
        hcl_config_parser = TerraformGraphParser()
        module, module_dependency_map, _ = hcl_config_parser.parse_hcl_module(resources_dir,
                                                                              self.source)
        local_graph = LocalGraph(module, module_dependency_map)
        local_graph._create_vertices()
        local_graph.calculate_encryption_attribute()
        all_attributes = [vertex.get_attribute_dict() for vertex in local_graph.vertices]
        for attribute_dict in all_attributes:
            [resource_type, resource_name] = decode_graph_property_value(
                attribute_dict[CustomAttributes.ID]).split(".")
            if resource_type in ENCRYPTION_BY_RESOURCE_TYPE:
                is_encrypted = json.loads(attribute_dict[CustomAttributes.ENCRYPTION])
                details = json.loads(attribute_dict[CustomAttributes.ENCRYPTION_DETAILS])
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
