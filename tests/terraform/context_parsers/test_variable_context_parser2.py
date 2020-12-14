import unittest
from checkov.terraform.parser import Parser
from checkov.terraform.context_parsers.registry import parser_registry
import os


class TestVariableContextParser(unittest.TestCase):

    def setUp(self):
        test_root_dir = os.path.dirname(os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/'
        tf_definitions = {}
        parsing_errors = {}
        Parser().parse_directory(directory=test_root_dir,
                                 out_definitions=tf_definitions,
                                 out_evaluations_context={},
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
        self.assertEqual(
            self.definitions_context[os.path.dirname(
                os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments').get('user_exists'), False)
        self.assertEqual(
            self.definitions_context[os.path.dirname(
                os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments').get('app_client_id'), 'Temp')


if __name__ == '__main__':
    unittest.main()
