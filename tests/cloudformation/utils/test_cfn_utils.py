import os
import unittest

from checkov.cloudformation.cfn_utils import get_folder_definitions, build_definitions_context
from checkov.cloudformation.parser.node import dict_node
from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = 'file_formats'


class TestCfnUtils(unittest.TestCase):

    def setUp(self):
        self.test_root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, RELATIVE_PATH))

        definitions, definitions_raw = get_folder_definitions(self.test_root_dir, None)
        self.definitions_context = build_definitions_context(definitions, definitions_raw, self.test_root_dir)

    def validate_definition_lines(self, definition: dict_node, start_line, end_line, code_lines):
        self.assertEqual(definition['start_line'], start_line)
        self.assertEqual(definition['end_line'], end_line)
        self.assertEqual(len(definition['code_lines']), code_lines)

    def test_parameters_value(self):
        # Asserting yaml file
        yaml_parameters = self.definitions_context[self.test_root_dir + '/test.yaml'][
                CloudformationTemplateSections.PARAMETERS.value]
        self.assertIsNotNone(yaml_parameters)
        self.assertEqual(len(yaml_parameters), 2)
        self.validate_definition_lines(yaml_parameters['KmsMasterKeyId'], 4, 7, 4)
        self.validate_definition_lines(yaml_parameters['DBName'], 8, 11, 4)
        # Asserting json file
        json_parameters = self.definitions_context[self.test_root_dir + '/test.json'][
                CloudformationTemplateSections.PARAMETERS.value]
        self.assertIsNotNone(json_parameters)
        self.assertEqual(len(json_parameters), 2)
        self.validate_definition_lines(json_parameters['KmsMasterKeyId'], 4, 8, 5)
        self.validate_definition_lines(json_parameters['DBName'], 9, 13, 5)

    def test_resources_value(self):
        yaml_resources = self.definitions_context[self.test_root_dir + '/test.yaml'][
                CloudformationTemplateSections.RESOURCES.value]
        self.assertIsNotNone(yaml_resources)
        self.assertEqual(len(yaml_resources), 2)
        self.validate_definition_lines(yaml_resources['MySourceQueue'], 13, 16, 4)
        self.validate_definition_lines(yaml_resources['MyDB'], 17, 26, 10)
        json_resources = self.definitions_context[self.test_root_dir + '/test.json'][
                CloudformationTemplateSections.RESOURCES.value]
        self.assertIsNotNone(json_resources)
        self.assertEqual(len(json_resources), 2)
        self.validate_definition_lines(json_resources['MySourceQueue'], 16, 21, 6)
        self.validate_definition_lines(json_resources['MyDB'], 22, 31, 10)

    def test_outputs_value(self):
        yaml_outputs = self.definitions_context[self.test_root_dir + '/test.yaml'][
                CloudformationTemplateSections.OUTPUTS.value]
        self.assertIsNotNone(yaml_outputs)
        self.assertEqual(len(yaml_outputs), 1)
        self.validate_definition_lines(yaml_outputs['DBAppPublicDNS'], 28, 30, 3)
        json_outputs = self.definitions_context[self.test_root_dir + '/test.json'][
                CloudformationTemplateSections.OUTPUTS.value]
        self.assertIsNotNone(json_outputs)
        self.assertEqual(len(json_outputs), 1)
        self.validate_definition_lines(json_outputs['DBAppPublicDNS'], 34, 37, 4)

    def test_skipped_check_exists(self):
        skipped_checks = self.definitions_context[self.test_root_dir + '/test.yaml'][
                CloudformationTemplateSections.RESOURCES.value]['MyDB']['skipped_checks']
        self.assertEqual(len(skipped_checks), 1)
        self.assertEqual(skipped_checks[0]['id'], 'CKV_AWS_16')
        self.assertEqual(skipped_checks[0]['suppress_comment'],
                         'Ensure all data stored in the RDS is securely encrypted at rest\\n\')')

if __name__ == '__main__':
    unittest.main()
