import json
import os
import unittest

from checkov.terraform.parser import Parser


class TestTerraformHcl(unittest.TestCase):

    def test_hcl1_parsing(self):
        self._load_and_test('hcl1_example.tf', 'hcl1_example_expected.json')

    def test_hcl2_parsing(self):
        self._load_and_test('hcl2_example.tf', 'hcl2_example_expected.json')

    def test_clean_definitions(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        tf_definitions = Parser._parse_tf_definitions(f'{current_dir}/skip_bad_tf_example.tf')
        assert len(tf_definitions['variable']) == 1
        assert 'okay' in tf_definitions['variable'][0]
        assert len(tf_definitions['module']) == 2
        assert 'bar' in tf_definitions['module'][0]
        assert 'okay' in tf_definitions['module'][1]

    def _load_and_test(self, test_file, test_expected_file):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        parser = Parser()
        parse_errors = {}
        result = parser.parse_file(f'{current_dir}/{test_file}', parse_errors)

        with open(f'{current_dir}/{test_expected_file}', 'r') as f:
            expected_result = json.load(f)
        self.assertEqual(len(parse_errors.keys()), 0)
        self.assertEqual(json.dumps(expected_result), json.dumps(result))


if __name__ == '__main__':
    unittest.main()
