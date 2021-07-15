import os
import unittest

from checkov.cloudformation.cfn_utils import get_folder_definitions, build_definitions_context
from checkov.cloudformation.parser.node import dict_node

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = '../file_formats/cfn_utils'


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
        parameters = self.definitions_context[self.test_root_dir + '/test_yaml.yaml'][
                'Parameters']
        self.assertIsNotNone(parameters)
        self.assertEqual(len(parameters), 2)
        self.validate_definition_lines(parameters['KmsMasterKeyId'], 4, 7, 4)
        self.validate_definition_lines(parameters['DBName'], 8, 11, 4)

    def test_resources_value(self):
        resources = self.definitions_context[self.test_root_dir + '/test_yaml.yaml'][
                'Resources']
        self.assertIsNotNone(resources)
        self.assertEqual(len(resources), 2)
        self.validate_definition_lines(resources['MySourceQueue'], 13, 16, 4)
        self.validate_definition_lines(resources['MyDB'], 17, 26, 10)

    def test_outputs_value(self):
        outputs = self.definitions_context[self.test_root_dir + '/test_yaml.yaml'][
                'Outputs']
        self.assertIsNotNone(outputs)
        self.assertEqual(len(outputs), 1)
        self.validate_definition_lines(outputs['DBAppPublicDNS'], 28, 30, 3)

    def test_skipped_check_exists(self):
        skipped_checks = self.definitions_context[self.test_root_dir + '/test_yaml.yaml'][
                'Resources']['MyDB']['skipped_checks']
        self.assertEqual(len(skipped_checks), 1)
        self.assertEqual(skipped_checks[0]['id'], 'CKV_AWS_16')
        self.assertEqual(skipped_checks[0]['suppress_comment'],
                         'Ensure all data stored in the RDS is securely encrypted at rest\\n\')')

if __name__ == '__main__':
    unittest.main()
