import unittest
from checkov.terraform.parser import Parser
from checkov.terraform.evaluation.evaluation_methods.const_variable_evaluation import ConstVariableEvaluation
from checkov.terraform.evaluation.base_variable_evaluation import BaseVariableEvaluation
from checkov.terraform.context_parsers.registry import parser_registry
import dpath.util
import os


class TestBaseVariableEvaluation(unittest.TestCase):

    def setUp(self):
        test_root_dir = os.path.dirname(os.path.realpath(__file__)) + '/resources/default_evaluation'
        tf_definitions = {}
        parsing_errors = {}
        definitions_context = {}
        Parser().hcl2(directory=test_root_dir, tf_definitions=tf_definitions, parsing_errors=parsing_errors)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        variable_evaluator = ConstVariableEvaluation(test_root_dir, tf_definitions, definitions_context)
        variable_evaluator.evaluate_variables()
        self.tf_definitions = variable_evaluator.tf_definitions
        self.definitions_context = variable_evaluator.definitions_context

    def test_extract_context_path(self):
        path = 'resource/0/aws_cognito_user_group/user_group/name/0'
        self.assertEqual(ConstVariableEvaluation.extract_context_path(path),
                         ('resource/aws_cognito_user_group/user_group', 'name'))

    def test_all_expressions_evaluated(self):
        self.assertEqual(
            len(dpath.get(self.definitions_context[
                              os.path.dirname(os.path.realpath(__file__)) + '/resources/default_evaluation/main.tf'],
                          'evaluations/dummy_1/definitions')),
            2)

    def test__is_variable_only_expression(self):
        entry_expression1 = "${local.dummy_with_comma}"
        assignment_regex1 = '((?:\\$\\{)?local\\.dummy_with_comma(?:\\})?)'
        entry_expression2 = "var.customer_name"
        assignment_regex2 = '((?:\\$\\{)?var\\.customer_name(?:\\})?)'
        entry_expression3 = "${var.customer_name}_with_more_stuff"
        assignment_regex3 = '((?:\\$\\{)?var\\.customer_name(?:\\})?)'
        self.assertTrue(BaseVariableEvaluation._is_variable_only_expression(assignment_regex1, entry_expression1))
        self.assertTrue(BaseVariableEvaluation._is_variable_only_expression(assignment_regex2, entry_expression2))
        self.assertFalse(BaseVariableEvaluation._is_variable_only_expression(assignment_regex3, entry_expression3))

    def test__generate_evaluation_regex(self):
        definition_type1, var_name1 = 'locals', 'dummy'
        definition_type2, var_name2 = 'variable', 'customer_name'
        self.assertEqual(BaseVariableEvaluation._generate_evaluation_regex(definition_type1, var_name1),
                         "((?:\$\{)?local[.]dummy(?:\})?)")
        self.assertEqual(BaseVariableEvaluation._generate_evaluation_regex(definition_type2, var_name2),
                         "((?:\$\{)?var[.]customer_name(?:\})?)")

    def tearDown(self):
        parser_registry.definitions_context = {}


if __name__ == '__main__':
    unittest.main()
