import pprint
from typing import List, Tuple
from unittest import TestCase

from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.utils import get_referenced_vertices_in_value, \
    replace_map_attribute_access_with_dot, generate_possible_strings_from_wildcards, \
    attribute_has_nested_attributes
from checkov.terraform.graph_builder.variable_rendering.vertex_reference import TerraformVertexReference
from checkov.terraform.graph_builder.local_graph import update_dictionary_attribute


class TestUtils(TestCase):
    def test_find_non_literal_values(self):
        aliases = {'aws': {CustomAttributes.BLOCK_TYPE: BlockType.PROVIDER}}
        str_value = 'aws.east1'
        expected = [TerraformVertexReference(BlockType.PROVIDER, ['aws', 'east1'], 'aws.east1')]
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
        expected = [
            [TerraformVertexReference(BlockType.VARIABLE, ['x'], 'var.x')],
            [TerraformVertexReference(BlockType.VARIABLE, ['x'], 'var.x')],
            [],
            [TerraformVertexReference(BlockType.RESOURCE, ['aws_instance.example', 'id'], 'aws_instance.example.id')],
            [TerraformVertexReference(BlockType.VARIABLE, ['customer_name'], 'var.customer_name')],
            [TerraformVertexReference(BlockType.LOCALS, ['role_name'], 'local.role_name'), TerraformVertexReference(BlockType.VARIABLE, ['profile'], 'var.profile'), TerraformVertexReference(BlockType.VARIABLE, ['region'], 'var.region')],
            [TerraformVertexReference(BlockType.RESOURCE, ['aws_vpc.main'], 'aws_vpc.main'), TerraformVertexReference(BlockType.RESOURCE, ['aws_vpc.main', 'cidr_block'], 'aws_vpc.main.cidr_block'), TerraformVertexReference(BlockType.VARIABLE, ['x'], 'var.x')],
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

    def test_update_dictionary_locals(self):
        origin_config = {'aws_s3_bucket': {'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['${var.acl}'], 'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
        key_to_update = 'acl'
        new_value = ['public-read']
        expected_config = {'aws_s3_bucket': {'destination': {'bucket': ['tf-test-bucket-destination-12345'], 'acl': ['public-read'], 'versioning': [{'enabled': ['${var.is_enabled}']}]}}}
        actual_config = update_dictionary_attribute(origin_config, key_to_update, new_value)
        self.assertEqual(expected_config, actual_config, f'failed to update config.\nexpected: {expected_config}\ngot: {actual_config}')

    def test_generate_possible_strings_from_wildcards(self):
        origin_string = "a.*.b.*.c.*"
        expected_results = [
            "a.0.b.0.c.0",
            "a.0.b.1.c.0",
            "a.1.b.0.c.0",
            "a.0.b.0.c.1",
            "a.1.b.1.c.0",
            "a.1.b.0.c.1",
            "a.0.b.1.c.1",
            "a.1.b.1.c.1",
            "a.b.c",
        ]
        expected_results.sort()
        results = generate_possible_strings_from_wildcards(origin_string=origin_string, max_entries=2)
        results.sort()
        self.assertEqual(expected_results, results)

    def test_find_var_blocks(self):
        cases: List[Tuple[str, List[TerraformVertexReference]]] = [
            (
                "${local.one}",
                [
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["one"], origin_value="local.one")
                ]
            ),
            (
                "${local.NAME[foo]}-${local.TAIL}${var.gratuitous_var_default}",
                [
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["NAME"], origin_value="local.NAME"),
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["TAIL"], origin_value="local.TAIL"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["gratuitous_var_default"], origin_value="var.gratuitous_var_default"),
                ]
            ),
            # Ordered returning of sub-vars and then outer var.
            (
                "${merge(local.common_tags,local.common_data_tags,{'Name': 'my-thing-${var.ENVIRONMENT}-${var.REGION}'})}",
                [
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["common_tags"], origin_value="local.common_tags"),
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["common_data_tags"], origin_value="local.common_data_tags"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["ENVIRONMENT"],
                                    origin_value="var.ENVIRONMENT"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["REGION"],
                                    origin_value="var.REGION"),
                ],
            ),
            (
                "${merge(${local.common_tags},${local.common_data_tags},{'Name': 'my-thing-${var.ENVIRONMENT}-${var.REGION}'})}",
                [
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["common_tags"], origin_value="local.common_tags"),
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["common_data_tags"],
                                    origin_value="local.common_data_tags"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["ENVIRONMENT"],
                                    origin_value="var.ENVIRONMENT"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["REGION"],
                                    origin_value="var.REGION"),
                ],
            ),
            (
                '${merge(var.tags, map("Name", "${var.name}", "data_classification", "none"))}',
                [
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["tags"],
                                    origin_value="var.tags"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["name"],
                                    origin_value="var.name"),
                ]
            ),
            (
                '${var.metadata_http_tokens_required ? "required" : "optional"}',
                [
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["metadata_http_tokens_required"],
                                    origin_value="var.metadata_http_tokens_required"),
                ]
            ),
            (
                '${local.NAME[${module.bucket.bucket_name}]}-${local.TAIL}${var.gratuitous_var_default}',
                [
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["NAME"],
                                    origin_value="local.NAME"),
                    TerraformVertexReference(BlockType.MODULE, sub_parts=["bucket", "bucket_name"],
                                    origin_value="module.bucket.bucket_name"),
                    TerraformVertexReference(BlockType.LOCALS, sub_parts=["TAIL"],
                                    origin_value="local.TAIL"),
                    TerraformVertexReference(BlockType.VARIABLE, sub_parts=["gratuitous_var_default"],
                                    origin_value="var.gratuitous_var_default"),
                ]
            ),
        ]
        for case in cases:
            actual = get_referenced_vertices_in_value(value=case[0], aliases={}, resources_types=[])
            assert actual == case[1], \
                f"Case \"{case[0]}\" failed ❌:\n" \
                f"  Expected: \n{pprint.pformat([str(c) for c in case[1]], indent=2)}\n\n" \
                f"  Actual: \n{pprint.pformat([str(c) for c in actual], indent=2)}"
            print(f"Case \"{case[0]}: ✅")

    def test__attribute_has_nested_attributes_dictionary(self):
        attributes = {'name': ['${var.lb_name}'], 'internal': [True], 'security_groups': ['${var.lb_security_group_ids}'], 'subnets': ['${var.subnet_id}'], 'enable_deletion_protection': [True], 'tags': {'Terraform': True, 'Environment': 'sophi-staging'}, 'resource_type': ['aws_alb'], 'tags.Terraform': True, 'tags.Environment': 'sophi-staging'}
        self.assertTrue(attribute_has_nested_attributes(attribute_key='tags', attributes=attributes))
        self.assertFalse(attribute_has_nested_attributes(attribute_key='name', attributes=attributes))
        self.assertFalse(attribute_has_nested_attributes(attribute_key='tags.Environment', attributes=attributes))

    def test__attribute_has_nested_attributes_list(self):
        attributes = {'most_recent': [True], 'filter': [{'name': 'name', 'values': ['amzn-ami-hvm-*-x86_64-gp2']}, {'name': 'owner-alias', 'values': ['amazon']}], 'filter.0': {'name': 'name', 'values': ['amzn-ami-hvm-*-x86_64-gp2']}, 'filter.0.name': 'name', 'filter.0.values': ['amzn-ami-hvm-*-x86_64-gp2'], 'filter.0.values.0': 'amzn-ami-hvm-*-x86_64-gp2', 'filter.1': {'name': 'owner-alias', 'values': ['amazon']}, 'filter.1.name': 'owner-alias', 'filter.1.values': ['amazon'], 'filter.1.values.0': 'amazon'}
        self.assertTrue(attribute_has_nested_attributes(attribute_key='filter', attributes=attributes))
        self.assertTrue(attribute_has_nested_attributes(attribute_key='filter.1.values', attributes=attributes))
        self.assertFalse(attribute_has_nested_attributes(attribute_key='filter.1.values.0', attributes=attributes))
