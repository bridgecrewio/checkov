import os
from unittest import TestCase

from checkov.terraform.variable_rendering.evaluate_terraform import evaluate_terraform, replace_string_value, \
    remove_interpolation


class TestTerraformEvaluation(TestCase):
    def test_directive(self):
        input_str = '"Hello, %{ if "d" != "" }named%{ else }unnamed%{ endif }!"'
        expected = 'Hello, named!'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_condition(self):
        input_str = '"2 > 0 ? bigger : smaller"'
        expected = 'bigger'
        self.assertEqual(expected, evaluate_terraform(input_str).strip())

        input_str = '"2 > 5 ? bigger : smaller"'
        expected = 'smaller'
        self.assertEqual(expected, evaluate_terraform(input_str).strip())

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

        input_str = 'regex(r"(\\d\\d\\d\\d)-(\\d\\d)-(\\d\\d)", "2019-02-01")'
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

    def test_concat_dictionaries(self):
        input_str = "concat([{'key':'a','value':'a'},{'key':'b','value':'b'}, \"{'key':'d','value':'d'}\"],,[{'key':'c','value':'c'}],)"
        expected = [{'key':'a','value':'a'},{'key':'b','value':'b'},"{'key':'d','value':'d'}",{'key':'c','value':'c'}]
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

    def test_merge2(self):
        input_str = 'merge({"a"="b", "c"="d"}, {"e"="f", "c"="z"}, {"r"="o", "t"="m"})'
        expected = {"a":"b", "c":"z","e":"f","r":"o","t":"m"}
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_merge_multiline(self):
        input_str = "merge(\n{'Tag1':'one','Tag2':'two'},\n{'Tag4' = 'four'},\n{'Tag2'='multiline_tag2'})"
        expected = {'Tag1': 'one', 'Tag2': 'multiline_tag2', 'Tag4': 'four'}
        self.assertEqual(expected, evaluate_terraform(input_str))


    def test_reverse(self):
        input_str = 'reverse([1, 2, 3])'
        expected = [3, 2, 1]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_sort(self):
        input_str = 'sort(compact(distinct(concat([\'postgresql-tcp\'],[],[\'\']))))'
        expected = ['postgresql-tcp']
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_condition2(self):
        input_str = 'us-west-2 == "something to produce false" ? true : false'
        expected = 'false'
        self.assertEqual(expected, evaluate_terraform(input_str).strip())

    def test_complex_merge(self):
        cases = [
            ("merge(local.one, local.two)",
             "merge(local.one, local.two)"),
            ("merge({\"Tag4\" = \"four\"}, {\"Tag5\" = \"five\"})",
             {"Tag4" : "four", "Tag5" : "five"}),
            ("merge({\"a\"=\"b\"}, {\"b\"=[1,2], \"c\"=\"z\"}, {\"d\"=3})",
             {"a":"b", "b":[1,2], "c":"z", "d":3}),
            ('merge({\'a\': \'}, evil\'})',
             {"a": '}, evil'}),
            ('merge(local.common_tags,,{\'Tag4\': \'four\'},,{\'Tag2\': \'Dev\'},)',
             'merge(local.common_tags,{\'Tag4\': \'four\'},{\'Tag2\': \'Dev\'},)')
        ]
        for case in cases:
            input_str = case[0]
            expected = input_str if case[1] is None else case[1]
            actual = evaluate_terraform(input_str)
            assert actual == expected, f"Case \"{input_str}\" failed. Expected: {expected}  Actual: {actual}"

    def test_map_access(self):
        input_str = '{\'module-input-bucket\':\'mapped-bucket-name\'}[module-input-bucket]-works-yay'
        expected = 'mapped-bucket-name-works-yay'
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = '{"module-input-bucket":"mapped-bucket-name"}[module-input-bucket]-works-yay'
        expected = 'mapped-bucket-name-works-yay'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_replace_with_map(self):
        original_str = '{\'module-input-bucket\':\'mapped-bucket-name\'}[module.bucket.name]-works-yay'
        replaced = replace_string_value(original_str, "module.bucket.name", "module-input-bucket", keep_origin=False)
        expected = '{\'module-input-bucket\':\'mapped-bucket-name\'}[module-input-bucket]-works-yay'
        self.assertEqual(expected, replaced)

    def test_replace_interpolation(self):
        original_str = '${mapped-bucket-name}[module.bucket.name]-works-yay'
        replaced = replace_string_value(original_str, "module.bucket.name", "module-input-bucket", keep_origin=False)
        expected = '${mapped-bucket-name}[module-input-bucket]-works-yay'
        self.assertEqual(expected, replaced)

    def test_remove_interpolation1(self):
        original_str = '${merge(local.common_tags,local.common_data_tags,{\'Name\':\'Bob-${local.static1}-${local.static2}\'})}'
        replaced = remove_interpolation(original_str)
        expected = 'merge(local.common_tags,local.common_data_tags,{\'Name\':\'Bob-local.static1-local.static2\'})'
        self.assertEqual(expected, replaced)

    def test_jsonencode(self):
        cases = [
            ("jsonencode(['a', 42, true, null])", ["a", 42, True, None]),
            ("jsonencode({'a': 'b'})", {"a": "b"}),
            ("jsonencode({'a' = 'b'})", {"a": "b"}),
            ("jsonencode({'a' = 42})", {"a": 42}),
            ("jsonencode({'a' = true})", {"a": True}),
            ("jsonencode({'a' = false})", {"a": False}),
            ("jsonencode({'a' = null})", {"a": None}),
            ("jsonencode({'a' = ['b', 'c']})", {"a": ["b", "c"]}),
            ("jsonencode({'a' = jsonencode(['b', 'c'])})", {"a": ["b", "c"]}),
        ]

        for input_str, expected in cases:
            with self.subTest(input_str):
                assert evaluate_terraform(input_str) == expected

    def test_block_file_write(self):
        temp_file_path = "/tmp/file_shouldnt_create"
        input_str = "[x for x in {}.__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.__builtins__['__import__']('os').system('date >> /tmp/file_shouldnt_create')"
        evaluated = evaluate_terraform(input_str)
        self.assertEqual(input_str, evaluated)
        self.assertFalse(os.path.exists(temp_file_path))

    def test_block_file_write2(self):
        temp_file_path = "/tmp/file_shouldnt_create_vuln"
        input_str = "(lambda: [x for x in {}.__class__.__bases__[0].__subclasses__() if x.__name__ == 'catch_warnings'][0]()._module.__builtins__['__import__']('os').system('date >> /tmp/file_shouldnt_create_vuln'))()"
        evaluated = evaluate_terraform(input_str)
        self.assertEqual(input_str, evaluated)
        self.assertFalse(os.path.exists(temp_file_path))

    def test_block_file_write_lower(self):
        temp_file_path = "/tmp/file_shouldnt_create"
        input_str = "[x for x in parsint.__bases__[0].__subclasses__()][134]()._module.__builtins__['__IMPORT__'.lower()]('os').system('date >> /tmp/file_shouldnt_create')"
        evaluated = evaluate_terraform(input_str)
        self.assertEqual(input_str, evaluated)
        self.assertFalse(os.path.exists(temp_file_path))

    def test_block_math_expr(self):
        input_str = "__import__('math').sqrt(25)"
        evaluated = evaluate_terraform(input_str)
        self.assertEqual(input_str, evaluated)

    def test_block_segmentation_fault(self):
        # in this test, the following code is causing segmentation fault if evaluated
        input_str = """
(lambda fc=(
    lambda n: [
        c for c in
            ().__class__.__bases__[0].__subclasses__()
            if c.__name__ == n
        ][0]
    ):
    fc("function")(
        fc("code")(
            0,0,0,0,0,b'test',(),(),(),"","",0,b'test'
        ),{}
    )()
)()
"""
        evaluated = evaluate_terraform(input_str)
        self.assertEqual(input_str.replace("\n", ""), evaluated)
