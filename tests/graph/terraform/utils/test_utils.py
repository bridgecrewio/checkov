from unittest import TestCase

from checkov.graph.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.graph.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.graph.terraform.utils.utils import replace_map_attribute_access_with_dot, get_referenced_vertices_in_value, \
    VertexReference, update_dictionary_attribute


class Test(TestCase):
    def test_find_non_literal_values(self):
        aliases = {'aws': {CustomAttributes.BLOCK_TYPE: BlockType.PROVIDER}}
        str_value = 'aws.east1'
        expected = [VertexReference(BlockType.PROVIDER, ['aws', 'east1'], 'aws.east1')]
        self.assertEqual(expected, get_referenced_vertices_in_value(str_value, aliases, []))

        str_values = [
                    'var.x',
                      'format("-%s", var.x)',
                      '../child',
                      'aws_instance.example.id',
                      'bc_c_${var.customer_name}',
                      'aws iam delete-role --role-name ${local.role_name} --profile ${var.profile} --region ${var.region}',
                      'length(aws_vpc.main) > 0 ? aws_vpc.main[0].cidr_block : ${var.x}',
                    ]
        expected =   [
                    [VertexReference(BlockType.VARIABLE, ['x'], 'var.x')],
                      [VertexReference(BlockType.VARIABLE, ['x'], 'var.x')],
                      [],
                      [VertexReference(BlockType.RESOURCE, ['aws_instance.example', 'id'], 'aws_instance.example.id')],
                      [VertexReference(BlockType.VARIABLE, ['customer_name'], 'var.customer_name')],
                      [VertexReference(BlockType.LOCALS, ['role_name'], 'local.role_name'), VertexReference(BlockType.VARIABLE, ['profile'], 'var.profile'), VertexReference(BlockType.VARIABLE, ['region'], 'var.region')],
                      [VertexReference(BlockType.RESOURCE, ['aws_vpc.main'], 'aws_vpc.main'), VertexReference(BlockType.RESOURCE, ['aws_vpc.main', 'cidr_block'], 'aws_vpc.main.cidr_block'), VertexReference(BlockType.VARIABLE, ['x'], 'var.x')],
        ]

        for i in range(0, len(str_values)):
            self.assertEqual(expected[i], get_referenced_vertices_in_value(str_values[i], aliases, ['aws_vpc', 'aws_instance']))

    def test_replace_map_attribute_access_with_dot(self):
        str_value = 'data.aws_availability_zones["available"].names[1]'
        replace_map_attribute_access_with_dot(str_value)
        self.assertEqual('data.aws_availability_zones.available.names[1]', replace_map_attribute_access_with_dot(str_value))

        str_value = 'data.aws_availability_zones[0].names[1]'
        replace_map_attribute_access_with_dot(str_value)
        self.assertEqual('data.aws_availability_zones[0].names[1]', replace_map_attribute_access_with_dot(str_value))

    def test_update_dictionary_attribute_nested(self):
        origin_config = {'aws_s3_bucket': {'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'], 'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
        key_to_update = 'versioning.enabled'
        new_value = [False]
        expected_config = {'aws_s3_bucket': {'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'], 'versioning': [{'enabled': [False]}]}}}
        actual_config = update_dictionary_attribute(origin_config, key_to_update, new_value)
        self.assertEqual(expected_config, actual_config, f'failed to update config. expected: {expected_config}, got: {actual_config}')

    def test_update_dictionary_attribute(self):
        origin_config = {'aws_s3_bucket': {'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'], 'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
        key_to_update = 'acl'
        new_value = ['public-read']
        expected_config = {'aws_s3_bucket': {'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['public-read'], 'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
        actual_config = update_dictionary_attribute(origin_config, key_to_update, new_value)
        self.assertEqual(expected_config, actual_config, f'failed to update config.\nexpected: {expected_config}\ngot: {actual_config}')
