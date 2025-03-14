import os
import unittest

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.terraform import TFDefinitionKey
from checkov.terraform.context_parsers.parsers.resource_context_parser import ResourceContextParser
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.AMICopyUsesCMK import check
from checkov.terraform.runner import Runner
from checkov.terraform.tf_parser import TFParser
from tests.terraform.context_parsers.mock_context_parser import MockContextParser

mock_tf_file = os.path.dirname(os.path.realpath(__file__)) + "/mock_tf_files/mock.tf"
mock_definition = (mock_tf_file, {"mock": [{"mock_type": {"mock_name": {"value": ["mock_value"]}}}]})

inline_tf_file = os.path.dirname(os.path.realpath(__file__)) + "/mock_tf_files/inline_suppression.tf"
mock_dir_path = os.path.dirname(os.path.realpath(__file__)) + "/mock_tf_files"


class TestBaseParser(unittest.TestCase):
    def test_enrich_definition_block(self):
        this_integration = BcPlatformIntegration()
        this_integration.get_public_run_config()
        metadata_integration.bc_integration = this_integration
        metadata_integration.pre_scan()
        mock_parser = MockContextParser()
        parser_registry.register(mock_parser)
        definition_context = parser_registry.enrich_definitions_context(mock_definition)
        skipped_checks = definition_context[mock_tf_file]["mock"]["mock_type"]["mock_name"].get("skipped_checks")
        self.assertIsNotNone(skipped_checks)
        self.assertEqual(len(skipped_checks), 3)
        # Ensure checkov IDs are mapped to BC IDs
        self.assertEqual(skipped_checks[2]["id"], "CKV_AWS_15")
        metadata_integration.bc_integration = bc_integration

    def test__compute_definition_end_line_with_multi_curly_brackets(self):
        # given
        mock_parser = MockContextParser()
        mock_parser.filtered_lines = [
            (1, '#data "aws_iam_policy_document" "null" {}'),
            (3, 'resource "aws_subnet" "pub_sub" {'),
            (4, "tags = merge({"),
            (5, 'Name = "${var.network_name}-pub-sub-${element(var.azs, count.index)}"'),
            (6, 'Tier = "public"'),
            (7, '}, var.tags, var.add_eks_tags ? { "kubernetes.io/role/elb" : "1" } : {})'),
            (8, "}"),
        ]
        mock_parser.filtered_line_numbers = [1, 3, 4, 5, 6, 7, 8]

        # when
        end_line_num = mock_parser._compute_definition_end_line(3)

        # then
        self.assertEqual(8, end_line_num)

    def test_inline_suppression(self):
        parser = TFParser()
        _, tf_definition = parser.parse_hcl_module(mock_dir_path,source='TERRAFORM')
        resources_parser = ResourceContextParser()
        parser_registry.register(resources_parser)
        inline_key = TFDefinitionKey(inline_tf_file)
        inline_suppression_definition = tf_definition[inline_key]
        definition_context = parser_registry.enrich_definitions_context((inline_key,inline_suppression_definition))

        aws_s3_bucket_resources = definition_context[inline_key]["resource"]["aws_s3_bucket"]

        self.assertEqual(len(aws_s3_bucket_resources["multi-line-multi-checks"].get("skipped_checks")), 3)
        self.assertEqual(len(aws_s3_bucket_resources["multi-line-no-comment"].get("skipped_checks")), 2)
        self.assertEqual(len(aws_s3_bucket_resources["one-line-one-check"].get("skipped_checks")), 1)
        self.assertEqual(len(aws_s3_bucket_resources["one-line-multi-checks"].get("skipped_checks")), 2)
        self.assertEqual(len(aws_s3_bucket_resources["no-comment"].get("skipped_checks")), 0)


if __name__ == "__main__":
    unittest.main()
