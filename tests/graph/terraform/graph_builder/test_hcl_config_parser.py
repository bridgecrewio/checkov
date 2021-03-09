import os
from unittest import TestCase

from checkov.graph.parser import TerraformGraphParser

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestTerraformGraphParser(TestCase):
    def test_bool_parsing_avoid_remove_non_existing(self):
        conf = {'test': ['Bool'], 'variable': ['aws:SecureTransport'], 'values': [['false']]}
        config_parser = TerraformGraphParser()
        actual = config_parser._hcl_boolean_types_to_boolean(conf)
        expected = {'test': ['Bool'], 'variable': ['aws:SecureTransport'], 'values': [[False]]}
        self.assertDictEqual(expected, actual)

    def test_bool_parsing_sort_only_lists(self):
        conf = {'enabled_metrics': [['a', 'c', 'b'], 'b', 'a', 'c']}
        config_parser = TerraformGraphParser()
        actual = config_parser._hcl_boolean_types_to_boolean(conf)
        expected = {'enabled_metrics': [['a', 'b', 'c'], 'a', 'b', 'c']}
        self.assertDictEqual(expected, actual)

    def test_bool_parsing_sort_only_lists_with_bools(self):
        conf = {'enabled_metrics': [['a', 'true', 'false'], 'b', 'true', 'false']}
        config_parser = TerraformGraphParser()
        actual = config_parser._hcl_boolean_types_to_boolean(conf)
        expected = {'enabled_metrics': [[True, False, 'a'], True, False, 'b']}
        self.assertDictEqual(expected, actual)
