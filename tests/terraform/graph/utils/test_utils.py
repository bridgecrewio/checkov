import pprint
from typing import List, Tuple
from unittest import TestCase

from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.utils import get_referenced_vertices_in_value, \
    replace_map_attribute_access_with_dot, generate_possible_strings_from_wildcards, \
    attribute_has_nested_attributes, get_reference_indexes_in_expressions
from checkov.terraform.graph_builder.variable_rendering.vertex_reference import TerraformVertexReference


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

    def test_get_reference_indexes_in_expressions(self):
        name = 'aws_lb_target_group.x'
        get_indexes = get_reference_indexes_in_expressions
        # literal indexes
        self.assertEqual({0}, get_indexes(['${aws_lb_target_group.x[0].arn}'], name))
        self.assertEqual({0, 2}, get_indexes(
            {'a': ['${aws_lb_target_group.x[0].arn}'], 'b': 'prefix-${aws_lb_target_group.x[2].arn}'}, name))
        self.assertEqual({1}, get_indexes("${jsonencode({'a': '${aws_lb_target_group.x[1].arn}', 'b': 'c'})}", name))
        self.assertEqual({1}, get_indexes('${aws_lb_target_group.x[ 1 ].arn}', name))
        self.assertEqual({1}, get_indexes('${aws_lb_target_group.x[1.0].arn}', name))
        self.assertEqual({1}, get_indexes('${aws_lb_target_group.x.1.arn}', name))
        self.assertEqual({1}, get_indexes('prefix-${aws_lb_target_group.x.1}', name))
        self.assertEqual({None}, get_indexes('${aws_lb_target_group.x.1a}', name))
        # uses without a literal index
        self.assertEqual({None}, get_indexes('${aws_lb_target_group.x[*].arn}', name))
        self.assertEqual({None}, get_indexes('${aws_lb_target_group.x[var.i].arn}', name))
        self.assertEqual({None}, get_indexes('${aws_lb_target_group.x["key"].arn}', name))
        self.assertEqual({None}, get_indexes('${length(aws_lb_target_group.x)}', name))
        self.assertEqual({None}, get_indexes('${aws_lb_target_group.x.*.arn}', name))
        # other names
        self.assertEqual(set(), get_indexes('${my_aws_lb_target_group.x[0].arn}', name))
        self.assertEqual(set(), get_indexes('${aws_lb_target_group.xy[0].arn}', name))
        self.assertEqual(set(), get_indexes('${aws_lb_target_group.x-y[0].arn}', name))
        self.assertEqual(set(), get_indexes('${data.aws_lb_target_group.x[0].arn}', name))
        self.assertEqual(set(), get_indexes(True, name))
        # plain text
        self.assertEqual(set(), get_indexes('see aws_lb_target_group.x for details', name))
        self.assertEqual(set(), get_indexes('see aws_lb_target_group.x[0] for details', name))
        self.assertEqual(set(), get_indexes('see length(aws_lb_target_group.x) for ${var.details}', name))
        self.assertEqual(set(), get_indexes('${upper("see aws_lb_target_group.x for details")}', name))
        self.assertEqual({1}, get_indexes('${aws_lb_target_group.x[1].arn} not aws_lb_target_group.x[2]', name))
        # template directives
        self.assertEqual({None}, get_indexes('%{ for x in aws_lb_target_group.x }${x.arn}%{ endfor }', name))
        self.assertEqual({0}, get_indexes('%{ if aws_lb_target_group.x[0].arn != "" }a%{ endif }', name))
        self.assertEqual(set(), get_indexes('%{ if var.a }aws_lb_target_group.x%{ endif }', name))
        self.assertEqual({None}, get_indexes('%{ if length({a=true}) > 0 && length(aws_lb_target_group.x) > 0 }a%{ endif }', name))
        self.assertEqual({0}, get_indexes('%{ if length({a=true}) > 0 && aws_lb_target_group.x[0].arn != "" }a%{ endif }', name))
        self.assertEqual(set(), get_indexes('%%{ if aws_lb_target_group.x }', name))
        # quotes and backslashes in the strings of an expression, as the parser stores them
        self.assertEqual({0}, get_indexes('${format("%s\\",aws_lb_target_group.x[0].arn)}', name))
        self.assertEqual({0}, get_indexes('${format("%s\\\\",aws_lb_target_group.x[0].arn)}', name))
        self.assertEqual({0}, get_indexes('${format("a\\"%s",aws_lb_target_group.x[0].arn)}', name))
        self.assertEqual({0}, get_indexes('${format("a\\\\\\"%s",aws_lb_target_group.x[0].arn)}', name))
        self.assertEqual({0}, get_indexes('${format("it\'s %s",aws_lb_target_group.x[0].arn)}', name))
        self.assertEqual({0}, get_indexes('${format("}{%s",aws_lb_target_group.x[0].arn)}', name))
        self.assertEqual({0}, get_indexes('it\'s a\\"${aws_lb_target_group.x[0].arn}', name))
        self.assertEqual(set(), get_indexes('${format("\\"aws_lb_target_group.x\\"",var.y)}', name))
        self.assertEqual(set(), get_indexes('$${aws_lb_target_group.x[0].arn}', name))
        # a backslash doesn't escape the start of a template sequence
        self.assertEqual({0}, get_indexes('${format("%s","C:\\${aws_lb_target_group.x[0].arn}")}', name))
        self.assertEqual(set(), get_indexes('${format("%s","C:\\$${aws_lb_target_group.x[0].arn}")}', name))
        # a heredoc in a function keeps its own quotes
        self.assertEqual(set(), get_indexes('${trimspace("see " aws_lb_target_group.x " for details")}', name))
        self.assertEqual(set(), get_indexes('${trimspace("a "b c" aws_lb_target_group.x[0] "d e"")}', name))
        self.assertEqual({0}, get_indexes('${trimspace("{"Resource": "${aws_lb_target_group.x[0].arn}"}")}', name))
        self.assertEqual({0}, get_indexes('${trimspace("a ${aws_lb_target_group.x[0].arn} "b"")}', name))
        self.assertEqual(set(), get_indexes('${trimspace("see " aws_lb_target_group.x for: details " end")}', name))
        self.assertEqual(set(), get_indexes('${trimspace("see ", aws_lb_target_group.x " end")}', name))
        self.assertEqual({0}, get_indexes('${trimspace("{"a": "b", "c": "${aws_lb_target_group.x[0].arn}"}")}', name))
        self.assertEqual({0}, get_indexes('${f(g("see "a" b"),aws_lb_target_group.x[0].arn,"c")}', name))
        self.assertEqual({0}, get_indexes('${trimspace("a "${aws_lb_target_group.x[0].arn}" b")}', name))
        self.assertEqual({0}, get_indexes('${trimspace("a "see ${aws_lb_target_group.x[0].arn}" b")}', name))
        self.assertEqual({0}, get_indexes('${trimspace("a "${aws_lb_target_group.x[0].arn} see" b")}', name))
        # strings in valid code
        self.assertEqual({0}, get_indexes('${"a" == aws_lb_target_group.x[0].arn ? "b" : "c"}', name))
        self.assertEqual({0}, get_indexes('${"5" - aws_lb_target_group.x[0].size - "2"}', name))
        self.assertEqual({0}, get_indexes('${[for s in "a" : "b" if s != aws_lb_target_group.x[0].arn || s == "c"]}', name))
        self.assertEqual({0}, get_indexes('${f("a", aws_lb_target_group.x[0].arn, "b")}', name))
        self.assertEqual({0}, get_indexes('${f("a\\"b", aws_lb_target_group.x[0].arn, "c\\"d")}', name))
        self.assertEqual({0}, get_indexes('${f("a", [for s in aws_lb_target_group.x[0].y : s], [for t in "b" : t])}', name))
        # both kinds of use
        self.assertEqual({1, None}, get_indexes('${try(aws_lb_target_group.x[1].arn, one(aws_lb_target_group.x[*].arn))}', name))
        # rendered values have no markers left
        self.assertEqual({0}, get_indexes('aws_lb_target_group.x[0].arn', name, is_rendered=True))
        self.assertEqual({None}, get_indexes('length(aws_lb_target_group.x)', name, is_rendered=True))
        self.assertEqual({0}, get_indexes('f("${aws_lb_target_group.x[0].arn}")', name, is_rendered=True))
        self.assertEqual({0}, get_indexes('f("it\'s aws_lb_target_group.x[0].arn")', name, is_rendered=True))
