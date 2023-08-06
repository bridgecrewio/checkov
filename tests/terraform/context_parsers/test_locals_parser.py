import unittest
from checkov.terraform.tf_parser import TFParser
from checkov.terraform.context_parsers.registry import parser_registry
import os


class TestLocalsContextParser(unittest.TestCase):

    def setup_dir(self, rel_path):
        test_root_dir = os.path.dirname(os.path.realpath(__file__)) + rel_path
        parsing_errors = {}
        definitions_context = {}
        tf_definitions = TFParser().parse_directory(directory=test_root_dir,
                                 out_parsing_errors=parsing_errors)
        for definition in tf_definitions.items():
            definitions_context = parser_registry.enrich_definitions_context(definition)
        return definitions_context

    def test_assignments_exists(self):
        definitions_context = self.setup_dir('/../evaluation/resources/default_evaluation/')
        assignments = definitions_context[os.path.dirname(os.path.realpath(__file__)) + '/../evaluation/resources/default_evaluation/main.tf']['locals']['assignments']
        self.assertIsNotNone(assignments)

        expected_assignments = {'dummy_with_dash': '${format("-%s",var.dummy_1)}', 'dummy_with_comma': '${format(":%s",var.dummy_1)}', 'bucket_name': '${var.bucket_name}'}

        for k, v in assignments.items():
            self.assertEqual(expected_assignments[k], v)

    def test_assignment_value(self):
        definitions_context = self.setup_dir('/../evaluation/resources/locals_evaluation/')
        assignments = definitions_context[
            os.path.dirname(os.path.realpath(__file__)) + '/../evaluation/resources/locals_evaluation/main.tf'][
            'locals'].get('assignments')
        self.assertIsNotNone(assignments)
        self.assertEqual(1, len(assignments.items()))
        for k, v in assignments.items():
            self.assertEqual(k, 'common_tags')
            self.assertIsInstance(v, dict)


if __name__ == '__main__':
    unittest.main()
