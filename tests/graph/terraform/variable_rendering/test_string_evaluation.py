from unittest import TestCase
from checkov.graph.terraform.variable_rendering.evaluate_terraform import evaluate_terraform


class TestTerraformEvaluation(TestCase):
    def test_directive(self):
        input_str = '"Hello, %{ if "d" != "" }named%{ else }unnamed%{ endif }!"'
        expected = 'Hello, named!'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_condition(self):
        input_str = '"2 > 0 ? bigger : smaller"'
        expected = 'bigger'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = '"2 > 5 ? bigger : smaller"'
        expected = 'smaller'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_format(self):
        input_str = '"format("Hello, %s!", "Ander")"'
        expected = 'Hello, Ander!'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = '"format("There are %d lights", 4)"'
        expected = 'There are 4 lights'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatlist(self):
        input_str = '"formatlist("Hello, %s!", ["Valentina", "Ander", "Olivia", "Sam"])"'
        expected = ['Hello, Valentina!', 'Hello, Ander!', 'Hello, Olivia!', 'Hello, Sam!']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_join(self):
        input_str = 'join(", ", ["foo", "bar", "baz"])'
        expected = 'foo, bar, baz'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'join(", ", ["foo"])'
        expected = 'foo'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_regex(self):
        input_str = 'regex("[a-z]+", "53453453.345345aaabbbccc23454")'
        expected = 'aaabbbccc'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'regex("[a-z]+", "53453453.34534523454")'
        expected = ''
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'regex("^(?:(?P<scheme>[^:/?#]+):)?(?://(?P<authority>[^/?#]*))?", "https://terraform.io/docs/")'
        expected = {"authority":"terraform.io", "scheme" : "https"}
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'regex("(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)", "2019-02-01")'
        expected = ["2019","02","01"]
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'regex("[a-z]+", "53453453.34534523454")'
        expected = ''
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_regexall(self):
        input_str = 'regexall("[a-z]+", "1234abcd5678efgh9")'
        expected = ["abcd","efgh"]
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'length(regexall("[a-z]+", "1234abcd5678efgh9"))'
        expected = 2
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'length(regexall("[a-z]+", "123456789")) > 0'
        expected = False
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_replace(self):
        input_str = 'replace("1 + 2 + 3", "+", "-")'
        expected = -4
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_substr(self):
        input_str = 'substr("hello world", 1, 4)'
        expected = 'ello'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_trim(self):
        input_str = 'trim("?!hello?!", "!?")'
        expected = 'hello'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_trimprefix(self):
        input_str = 'trimprefix("helloworld", "hello")'
        expected = 'world'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_upper(self):
        input_str = 'upper("hello")'
        expected = 'HELLO'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'upper("алло!")'
        expected = 'АЛЛО!'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_chunklist(self):
        input_str = 'chunklist(["a", "b", "c", "d", "e"], 2)'
        expected = [["a", "b"], ["c", "d"], ["e"]]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_coalese(self):
        input_str = 'coalesce("a", "b")'
        expected = 'a'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'coalesce("", "b")'
        expected = 'b'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'coalesce(1, 2)'
        expected = 1
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_coalescelist(self):
        input_str = 'coalescelist(["a", "b"], ["c", "d"])'
        expected = ['a', 'b']
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'coalescelist([], ["c", "d"])'
        expected = ["c", "d"]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_compact(self):
        input_str = 'compact(["a", "", "b", "c"])'
        expected = ['a', 'b', 'c']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_concat(self):
        input_str = 'concat(["a", ""], ["b", "c"])'
        expected = ['a', '', 'b', 'c']
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'concat([\'postgresql-tcp\'],[],[\'\'])'
        expected = ['postgresql-tcp', '']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_distinct(self):
        input_str = 'distinct(["a", "b", "a", "c", "d", "b"])'
        expected = ['a', 'b', 'c', 'd']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_flatten(self):
        input_str = 'flatten([["a", "b"], [], ["c"]])'
        expected = ['a', 'b', 'c']
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'flatten([[["a", "b"], []], ["c"]])'
        expected = ['a', 'b', 'c']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_index(self):
        input_str = 'index(["a", "b", "c"], "b")'
        expected = 1
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_keys(self):
        input_str = 'keys({"a"="ay", "b"="bee"})'
        expected = ["a", "b"]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_list(self):
        input_str = 'list("a", "b", "c")'
        expected = ['a', 'b', 'c']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_lookup(self):
        input_str = 'lookup({"a"="ay", "b"="bee"}, "a", "what?")'
        expected = 'ay'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_matchkeys(self):
        input_str = 'matchkeys(["i-123", "i-abc", "i-def"], ["us-west", "us-east", "us-east"], ["us-east"])'
        expected = ["i-abc", "i-def"]
        actual = evaluate_terraform(input_str)
        for elem in actual:
            if elem not in expected:
                self.fail(f'expected to find {elem} in {expected}. Got {actual}')

    def test_merge(self):
        input_str = 'merge({"a"="b", "c"="d"}, {"e"="f", "c"="z"})'
        expected = {"a":"b", "c":"z","e":"f"}
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_reverse(self):
        input_str = 'reverse([1, 2, 3])'
        expected = [3, 2, 1]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_sort(self):
        input_str = 'sort(compact(distinct(concat([\'postgresql-tcp\'],[],[\'\']))))'
        expected = ['postgresql-tcp']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_condition(self):
        input_str = 'us-west-2 == "something to produce false" ? true : false'
        expected = 'false'
        self.assertEqual(expected, evaluate_terraform(input_str))
