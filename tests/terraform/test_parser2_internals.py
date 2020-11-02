import unittest

from checkov.terraform import parser2


class TestParser2Internals(unittest.TestCase):
    def test_eval_string_to_list(self):
        expected = ["a", "b", "c"]
        assert parser2._eval_string('["a", "b", "c"]') == expected
