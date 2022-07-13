import os
import unittest
from checkov.common.parsers.json import parse

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestJsonParser(unittest.TestCase):
    def test_json_parser_lines(self):
        test_file = current_dir + "/resources/file1.json"
        cfn_dict, cfn_str = parse(test_file)

        resources = cfn_dict.get('Resources')
        bucket = resources.get('S3Bucket')
        properties = bucket.get('Properties')

        assert resources.start_mark.line == 2
        assert resources.end_mark.line == 31

        assert bucket.start_mark.line == 3
        assert bucket.end_mark.line == 30

        assert properties.start_mark.line == 5
        assert properties.end_mark.line == 28
