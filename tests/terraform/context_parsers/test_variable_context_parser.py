import unittest
from checkov.terraform.tf_parser import TFParser
from checkov.terraform.context_parsers.registry import parser_registry
import os


class TestVariableContextParser(unittest.TestCase):
    def setUp(self):
        test_root_dir = os.path.dirname(os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/'
        parsing_errors = {}
        tf_definitions = TFParser().parse_directory(directory=test_root_dir,
                                  out_parsing_errors=parsing_errors)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        self.definitions_context = definitions_context

    def test_assignments_exists(self):
        self.assertIsNotNone(
            self.definitions_context[os.path.dirname(
                os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments'))

    def test_assignment_value(self):
        self.assertFalse(
            self.definitions_context[os.path.dirname(
                os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments').get('user_exists')
        )
        self.assertEqual(
            self.definitions_context[os.path.dirname(
                os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments').get('app_client_id'), 'Temp')


if __name__ == '__main__':
    unittest.main()
