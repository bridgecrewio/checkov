import os
import unittest

from checkov.terraform.tf_parser import TFParser


class TestFileVsDirParser(unittest.TestCase):

    def test_file_dir_parser_results_match(self):
        parser = TFParser()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = current_dir + '/resources/parse_file_vs_dir/main.tf'
        dir_path = current_dir + '/resources/parse_file_vs_dir'
        tf_definitions_file = parser.parse_file(file_path, {})
        _, tf_definitions_dir = parser.parse_hcl_module(dir_path, 'terraform')
        self.assertDictEqual(tf_definitions_file, tf_definitions_dir.get(list(tf_definitions_dir.keys())[0]))

    def test_tofu_file_parsed_like_tf(self):
        parser = TFParser()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        tf_file_path = current_dir + '/resources/parse_file_vs_dir/main.tf'
        tofu_file_path = current_dir + '/resources/parse_file_vs_dir/main.tofu'

        tf_definitions = parser.parse_file(tf_file_path, {})
        tofu_definitions = parser.parse_file(tofu_file_path, {})

        self.assertDictEqual(tf_definitions, tofu_definitions)


if __name__ == '__main__':
    unittest.main()
