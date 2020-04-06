import unittest
from checkov.terraform.parser import Parser
from checkov.terraform.evaluation.evaluation_methods.const_variable_evaluation import ConstVariableEvaluation
from checkov.terraform.context_parsers.registry import parser_registry
import dpath.util
import os


class TestConstVariableEvaluation(unittest.TestCase):

    def setUp(self):
        test_root_dir = os.path.dirname(os.path.realpath(__file__)) + '/../resources/default_evaluation'
        tf_definitions = {}
        parsing_errors = {}
        Parser().hcl2(directory=test_root_dir, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        variable_evaluator = ConstVariableEvaluation(test_root_dir, tf_definitions, definitions_context)
        variable_evaluator.evaluate_variables()
        self.tf_definitions = variable_evaluator.tf_definitions
        self.definitions_context = variable_evaluator.definitions_context

    def test_evaluate_variables(self):
        self.assertEqual(
            dpath.get(self.tf_definitions[
                          os.path.dirname(os.path.realpath(__file__)) + '/../resources/default_evaluation/main.tf'],
                      'resource/0/aws_cognito_user_group/user_group/name/0'),
            'Pavel_Checkov_group')

    def test_all_expressions_evaluated(self):
        self.assertEqual(
            len(dpath.get(self.definitions_context[
                              os.path.dirname(os.path.realpath(__file__)) + '/../resources/default_evaluation/main.tf'],
                          'evaluations/dummy_1/definitions')),
            2)

    def tearDown(self):
        parser_registry.definitions_context = {}


if __name__ == '__main__':
    unittest.main()
