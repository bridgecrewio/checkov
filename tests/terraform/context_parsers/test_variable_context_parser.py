import unittest
from checkov.terraform.parser import Parser
from checkov.terraform.context_parsers.registry import parser_registry


class TestVariableContextParser(unittest.TestCase):

    def setUp(self):
        test_root_dir = 'tests/terraform/evaluation/resources/default_evaluation'
        tf_definitions = {}
        parsing_errors = {}
        Parser().hcl2(directory=test_root_dir, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        self.definitions_context = definitions_context

    def test_assignments_exists(self):
        self.assertIsNotNone(
            self.definitions_context['tests/terraform/evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments'))

    def test_assignment_value(self):
        self.assertEqual(
            self.definitions_context['tests/terraform/evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments').get('user_exists'), False)
        self.assertEqual(
            self.definitions_context['tests/terraform/evaluation/resources/default_evaluation/variables.tf'][
                'variable'].get(
                'assignments').get('app_client_id'), 'Temp')


if __name__ == '__main__':
    unittest.main()
