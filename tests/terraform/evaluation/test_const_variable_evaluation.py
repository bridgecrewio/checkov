import unittest
from checkov.terraform.parser import Parser
from checkov.terraform.evaluation.evaluation_methods.const_variable_evaluation import ConstVariableEvaluation
from checkov.terraform.context_parsers.registry import parser_registry
import dpath.util


class TestConstVariableEvaluation(unittest.TestCase):

    def setUp(self):
        test_root_dir = 'tests/terraform/evaluation/resources/default_evaluation'
        tf_definitions = {}
        parsing_errors = {}
        Parser().hcl2(directory=test_root_dir, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        variable_evaluator = ConstVariableEvaluation(tf_definitions, definitions_context)
        variable_evaluator.evaluate_variables()
        self.tf_definitions = variable_evaluator.tf_definitions
        self.definitions_context = variable_evaluator.definitions_context

    def test_evaluate_variables(self):
        self.assertEqual(
            dpath.get(self.tf_definitions['tests/terraform/evaluation/resources/default_evaluation/main.tf'],
                      'resource/0/aws_cognito_user_group/user_group/name/0'),
            'Pavel_Checkov_group')

    def test__extract_context_path(self):
        path = 'resource/0/aws_cognito_user_group/user_group/name/0'
        self.assertEqual(ConstVariableEvaluation._extract_context_path(path),
                         ('resource/aws_cognito_user_group/user_group', 'name'))

    def test_all_expressions_evaluated(self):
        self.assertEqual(
            len(dpath.get(self.definitions_context['tests/terraform/evaluation/resources/default_evaluation/main.tf'],
                          'locals/evaluations/dummy_1/expressions')),
            2)

    def tearDown(self):
        parser_registry.definitions_context = {}

if __name__ == '__main__':
    unittest.main()
