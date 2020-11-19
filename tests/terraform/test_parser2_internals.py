import unittest

from checkov.terraform import parser


class TestParserInternals(unittest.TestCase):
    def test_eval_string_to_list(self):
        expected = ["a", "b", "c"]
        assert parser._eval_string('["a", "b", "c"]') == expected
