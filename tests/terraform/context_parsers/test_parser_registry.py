import unittest

from checkov.terraform.context_parsers.registry import parser_registry
from tests.terraform.context_parsers.mock_context_parser import MockContextParser
import os

mock_definition = (os.path.dirname(os.path.realpath(__file__)) + '/mock_tf_files/mock.tf', {'mock': [
    {
        'mock_type': {
            'mock_name': {
                'value': [
                    'mock_value']}}}
]})


class TestScannerRegistry(unittest.TestCase):

    def test_enrich_definition_block(self):
        mock_parser = MockContextParser()
        parser_registry.register(mock_parser)
        definition_context = parser_registry.enrich_definitions_context(mock_definition)
        self.assertIsNotNone(definition_context[mock_definition[0]]['mock']['mock_type']['mock_name'])


if __name__ == '__main__':
    unittest.main()
