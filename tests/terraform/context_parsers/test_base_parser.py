import unittest

from tests.terraform.context_parsers.mock_context_parser import MockContextParser
from checkov.terraform.context_parsers.registry import parser_registry


mock_tf_file = 'tests/terraform/context_parsers/mock_tf_files/mock.tf'
mock_definition = ('tests/terraform/context_parsers/mock_tf_files/mock.tf', {'mock': [
    {
        'mock_type': {
            'mock_name': {
                'value': [
                    'mock_value']}}}
]})


class TestBaseParser(unittest.TestCase):

    def test_enrich_definition_block(self):
        mock_parser = MockContextParser()
        parser_registry.register(mock_parser)
        definition_context = parser_registry.enrich_definitions_context(mock_definition)
        self.assertIsNotNone(definition_context[mock_tf_file]['mock_type']['mock_name'].get('skipped_checks'))
        self.assertEqual(len(definition_context[mock_tf_file]['mock_type']['mock_name'].get('skipped_checks')),2)
        pass

if __name__ == '__main__':
    unittest.main()
