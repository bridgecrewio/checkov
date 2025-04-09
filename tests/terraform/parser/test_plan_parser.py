import os
import unittest
from pathlib import Path
from unittest import mock

from pytest_mock import MockerFixture

from checkov.common.util.consts import TRUE_AFTER_UNKNOWN
from checkov.terraform.plan_parser import parse_tf_plan
from checkov.common.parsers.node import StrNode

class TestPlanFileParser(unittest.TestCase):

    def test_tags_values_are_flattened(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_tags/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        file_resource_definition = tf_definition['resource'][0]
        resource_definition = next(iter(file_resource_definition.values()))
        resource_attributes = next(iter(resource_definition.values()))
        resource_tags = resource_attributes['tags'][0]
        for tag_key, tag_value in resource_tags.items():
            if tag_key not in ['__startline__', '__endline__', 'start_line', 'end_line']:
                self.assertIsInstance(tag_value, StrNode)

    def test_provider_is_included(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_tags/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        file_provider_definition = tf_definition['provider']
        self.assertTrue(file_provider_definition)  # assert a provider exists
        assert file_provider_definition[0].get('aws', {}).get('region', None) == ['us-west-2']
    
    def test_plan_multiple_providers(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_multiple_providers/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        providers = tf_definition['provider']
        self.assertEqual( len(providers), 3)
        provider_keys = []
        provider_aliases = []
        provider_addresses = []
        for provider in providers:
            key = next(iter(provider))
            provider_keys.append(key)
            provider_aliases.append( provider[key]['alias'][0] )
            provider_addresses.append( provider[key]['__address__'] )
        
        self.assertEqual(provider_keys, ["aws", "aws.ohio", "aws.oregon"])
        self.assertEqual(provider_aliases, ["default", "ohio", "oregon"])
        self.assertEqual(provider_addresses, ["aws.default", "aws.ohio", "aws.oregon"])

    def test_more_tags_values_are_flattened(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_tags_variety/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        # TODO: this should also verify the flattening but at least shows it parses now.
        assert True

    # Check Plan Booleans are treated similar to normal Terraform Parser
    # https://github.com/bridgecrewio/checkov/issues/1764
    def test_simple_type_booleans_clean(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_booleans/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        file_resource_definition = tf_definition['resource'][0]
        resource_definition = next(iter(file_resource_definition.values()))
        resource_attributes = next(iter(resource_definition.values()))
        self.assertTrue(resource_attributes['metadata'][0]['a'][0])
        self.assertTrue(resource_attributes['metadata'][0]['b'][0])
        self.assertFalse(resource_attributes['metadata'][0]['c'][0])
        self.assertFalse(resource_attributes['metadata'][0]['d'][0])

    def test_encodings(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        plan_files = ['tfplan_mac_utf8.json', 'tfplan_win_utf8.json', 'tfplan_win_utf16.json']

        for plan_file in plan_files:
            plan_path = os.path.join(current_dir, "resources", "plan_encodings", plan_file)
            tf_definition, _ = parse_tf_plan(plan_path, {})
            self.assertEqual(list(tf_definition['resource'][0].keys())[0], "aws_s3_bucket")

    def test_provisioners(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        plan_files = ['tfplan.json','tfplan2.json']

        for file in plan_files:
            valid_plan_path = current_dir + "/resources/plan_provisioners/" + file
            tf_definition, _ = parse_tf_plan(valid_plan_path, {})
            file_resource_definition = tf_definition['resource'][0]
            resource_definition = next(iter(file_resource_definition.values()))
            resource_attributes = next(iter(resource_definition.values()))
            self.assertTrue(resource_attributes['provisioner'])

    def test_module_with_connected_resources(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_module_with_connected_resources/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        file_resource_definition = tf_definition['resource'][1]
        resource_definition = next(iter(file_resource_definition.values()))
        resource_attributes = next(iter(resource_definition.values()))
        self.assertTrue(resource_attributes['references_'])

    @mock.patch.dict(os.environ, {"EVAL_TF_PLAN_AFTER_UNKNOWN": "True"})
    def test_after_unknown_handling(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_after_unknown/tfplan.json"
        tf_definition, _ = parse_tf_plan(valid_plan_path, {})
        file_resource_definition = tf_definition['resource'][0]
        resource_definition = next(iter(file_resource_definition.values()))
        resource_attributes = next(iter(resource_definition.values()))
        self.assertEqual(resource_attributes['logging_config'][0]["bucket"], [TRUE_AFTER_UNKNOWN])

def test_large_file(mocker: MockerFixture):
    # given
    test_file = Path(__file__).parent / "resources/plan_encodings/tfplan_mac_utf8.json"

    mocker.patch("checkov.cloudformation.parser.cfn_yaml.MAX_IAC_FILE_SIZE", 1)

    # when
    tf_definition, _ = parse_tf_plan(str(test_file), {})

    assert tf_definition['resource'][0]['aws_s3_bucket']['b']['start_line'][0] == 0
    assert tf_definition['resource'][0]['aws_s3_bucket']['b']['end_line'][0] == 0


if __name__ == '__main__':
    unittest.main()
