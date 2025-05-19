import os
from unittest import TestCase, mock
from datetime import datetime

import pytest

from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform, \
    replace_string_value, \
    remove_interpolation, _find_new_value_for_interpolation
from checkov.terraform.graph_builder.variable_rendering.safe_eval_functions import evaluate, get_asteval


class TestTerraformEvaluation(TestCase):
    def test_zipmap(self):
        input_str = '"zipmap(["a", "b"], [1, 2])"'
        expected = {'a': 1, 'b': 2}
        self.assertEqual(expected, evaluate_terraform(input_str))

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

    def test_conditional_expression(self):
        input_str = '"[\'${blocked == "allowed" ? True : False}\']"'
        expected = False
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = '${blocked == "allowed" ? True : False}'
        expected = False
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'blocked == "allowed" ? True : False'
        expected = False
        self.assertEqual(expected, evaluate_terraform(input_str))
        
        input_str = 'True == "true" ? True : False'
        expected = True
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = 'False != "false" ? True : False'
        expected = False
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
        expected = {"authority":"terraform.io", "scheme": "https"}
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

    def test_merge_interpolation(self):
        input_str = '${merge({\'environment\':\'${var.environment}\',\'name\':\'${local.cluster_name}\',\'role\':\'${var.role}\',\'team\':\'${var.team}\'})}'
        expected = {'environment': 'var.environment', 'name': 'local.cluster_name', 'role': 'var.role', 'team': 'var.team'}
        actual = evaluate_terraform(input_str, keep_interpolations=False)
        self.assertEqual(expected, actual)


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
            ("merge(local.one, local.two)", "merge(local.one, local.two)"),
            ('merge({"Tag4" = "four"}, {"Tag5" = "five"})', {"Tag4": "four", "Tag5": "five"}),
            ('merge({"a"="b"}, {"b"=[1,2], "c"="z"}, {"d"=3})', {"a": "b", "b": [1, 2], "c": "z", "d": 3}),
            ("merge({'a': '}, evil'})", {"a": "}, evil"}),
            (
                "merge(local.common_tags,,{'Tag4': 'four'},,{'Tag2': 'Dev'},)",
                "merge(local.common_tags,{'Tag4': 'four'},{'Tag2': 'Dev'},)",
            ),
        ]
        for case in cases:
            input_str = case[0]
            expected = input_str if case[1] is None else case[1]
            actual = evaluate_terraform(input_str)
            assert actual == expected, f'Case "{input_str}" failed. Expected: {expected}  Actual: {actual}'

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

    def test_evaluate_(self):
        input_str = '"10\\.0\\.\\0.\\0/8"'
        expected = '10\\.0\\.\\0.\\0/8'
        evaluated = evaluate_terraform(input_str)
        self.assertEqual(expected, evaluated)

    # Date Function
    @mock.patch('checkov.terraform.graph_builder.variable_rendering.safe_eval_functions.datetime')
    def test_timestamp(self,mock_dt):
        testdt = datetime(2018, 5, 13, 7, 44, 12, 0)
        mock_dt.utcnow = mock.Mock(return_value=testdt)
        input_str = 'timestamp()'
        expected = "2018-05-13T07:44:12Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_hours(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","24h")'
        expected = "2018-05-14T07:44:12Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_negative_hours(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","-24h")'
        expected = "2018-05-12T07:44:12Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_partialhours(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","1.5h")'
        expected = "2018-05-13T09:14:12Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_minutes(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","16m")'
        expected = "2018-05-13T08:00:12Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_hours_and_minutes(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","1h16m")'
        expected = "2018-05-13T09:00:12Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_hours_and_minutes_and_seconds(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","1h16m49s")'
        expected = "2018-05-13T09:01:01Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_hours_and_minutes_and_seconds_milliseconds(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","1h16m49s1001ms")'
        expected = "2018-05-13T09:01:02Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_timeadd_hours_and_minutes_and_seconds_milliseconds_microseconds(self):
        input_str = 'timeadd("2018-05-13T07:44:12Z","1h16m49s1001ms1000001us")'
        expected = "2018-05-13T09:01:03Z"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdatesimple(self):
        input_str = 'formatdate("HH:mm", "2018-01-02T23:12:01Z")'
        expected = '11:12'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_simple_and_am(self):
        input_str = 'formatdate("HH:mmaa", "2018-01-02T23:12:01Z")'
        expected = '11:12pm'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_more_complex(self):
        input_str = 'formatdate("DD MMM YYYY hh:mm", "2018-01-02T23:12:01Z")'
        expected = '02 Jan 2018 23:12'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_with_day(self):
        input_str = 'formatdate("EEE, DD MMM YYYY hh:mm:ss ZZZZZ", "2018-01-02T23:12:01-08:00")'
        expected = 'Tue, 02 Jan 2018 23:12:01 -08:00'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_utc_and_zzz(self):
        input_str = 'formatdate("DD MMM YYYY hh:mm ZZZ", "2018-01-02T23:12:01Z")'
        expected = '02 Jan 2018 23:12 UTC'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_utc_and_z(self):
        input_str = 'formatdate("DD MMM YYYY hh:mm Z", "2018-01-02T23:12:01Z")'
        expected = '02 Jan 2018 23:12 Z'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_with_day_utc(self):
        input_str = 'formatdate("EEE, DD MMM YYYY hh:mm:ss ZZZ", "2018-01-02T23:12:01-00:00")'
        expected = 'Tue, 02 Jan 2018 23:12:01 UTC'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_everything(self):
        input_str = 'formatdate("YYYY YY MMMM MMM MM M DD EEEE EEE hh h HH H AA aa mm m ss s ZZZZZ ZZZZ ZZZ Z", "2018-01-02T23:12:01-00:00")'
        expected = '2018 18 January Jan 01 1 02 Tuesday Tue 23 23 11 11 PM pm 12 12 01 1 +00:00 +0000 UTC Z'
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_simple_and_quotes(self):
        input_str = 'formatdate("HH \'o\'\'clock\'", "2018-01-02T23:12:01Z")'
        expected = "11 o'clock"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_formatdate_simple_and_more_quotes(self):
        input_str = 'formatdate("HH \'Hours and \'M \'Minute(s)\'", "2018-01-02T23:12:01Z")'
        expected = "11 Hours and 1 Minute(s)"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_handle_for_loop_in_dict(self):
        input_str = "{for val in [{'name': 'key3'},{'name': 'key4'}] : val.name => true}"
        expected = {'key3': 'true', 'key4': 'true'}
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_handle_for_loop_in_list(self):
        input_str = "[for val in ['k', 'v'] : val]"
        expected = ['k', 'v']
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = "{for val in ['k', 'v'] : val.name => true}"
        expected = "{for val in ['k', 'v'] : val.name :> true}"
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_handle_for_loop_in_list_of_dicts(self):
        input_str = "[for val in [{'name': 'raw', 'type': 'container'}, {'name': 'masked', 'type': 'blob'}] : {'name': '${val.name}', 'type': '${val.type}'}]"
        expected = [{'name': 'raw', 'type': 'container'}, {'name': 'masked', 'type': 'blob'}]
        self.assertEqual(expected, evaluate_terraform(input_str))

        input_str = "[for val in [{'a': 123, 'b': True, 'c': None}] : {'a': '${val.a}', 'b': '${val.b}', 'c': '${val.c}'}]"
        expected = [{'a': 123, 'b': True, 'c': None}]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_base64_value(self):
        input_str = "\"['dGVzdA==']\""
        expected = ["dGVzdA=="]
        self.assertEqual(expected, evaluate_terraform(input_str))

    def test_try_block(self):
        input_str = 'try("local.foo.boop", "{}")'
        expected = {}
        result = evaluate_terraform(input_str)
        self.assertEqual(expected, result)

    def test_try_then_merge_block(self):
        input_str = "try((merge({}, {})), 1, 2)"
        expected = {}
        result = evaluate_terraform(input_str)
        self.assertEqual(expected, result)

    def test_empty_string(self):
        input_str = "   "
        expected = input_str
        result = evaluate_terraform(input_str)
        self.assertEqual(expected, result)

        input_str = ""
        expected = input_str
        result = evaluate_terraform(input_str)
        self.assertEqual(expected, result)

    def test_dict_as_string(self):
        expected = {'Statement': [
            {'Action': ['lambda:CreateFunction', 'lambda:CreateEventSourceMapping', 'dynamodb:CreateTable'],
             'Effect': 'Allow', 'Resource': '*'}], 'Version': '2012-10-17'}
        input_str = '  {    "Version": "2012-10-17",    "Statement": [      {        "Effect": "Allow",        "Action": [          "lambda:CreateFunction",          "lambda:CreateEventSourceMapping",          "dynamodb:CreateTable",        ],        "Resource": "*"      }    ]  }'
        result = evaluate_terraform(input_str)
        assert result == expected


@pytest.mark.parametrize(
    "origin_str,str_to_replace,new_value,expected",
    [
        ("${lookup({'a': ${local.protocol1}},\"a\",\"https\")}", '${local.protocol1}', 'local.protocol1', "'local.protocol1'"),
        ('${length(keys(var.identity)) > 0 ? [${var.identity}] : []}', '${var.identity}', 'var.identity', 'var.identity'),
    ],
    ids=["escaped", "not escaped"],
)
def test_find_new_value_for_interpolation(origin_str: str, str_to_replace: str, new_value: str, expected: str):
    actual = _find_new_value_for_interpolation(origin_str, str_to_replace, new_value)
    assert actual == expected


def test_evaluate_range_pattern() -> None:

    # Test range pattern
    assert evaluate("1-10") == "1-10"
    assert evaluate("5-25")== "5-25"
    assert evaluate("10-5") == 5

    # Test non-range pattern for comparison
    assert evaluate("1+1") == 2


EVAL_DANGEROUS_INPUTS = [
    ("unicode_characters", "[{}._﹎class_﹎._﹎bases_﹎[0]._﹎subclasses_﹎()]"),
    ("generators_to_bypass_protections_code", "((gen:=(gen_list[0].gi_frame.f_back.f_back.f_globals for _ in [1,]),v:=gen_list.append(gen), gen_list[0])[2] for gen_list in [[]]).send(None).send(None).get('_'+'_builtins_'+'_')['_'+'_import_'+'_']('os').system('date >> /tmp/gen-example')"),
    ("system command", "__import__('os').system('rm -rf /')"),
    ("read passwd", "open('/etc/passwd').read()"),
    ("access builtins", "__builtins__.__import__('os').listdir('.')"),
    ("exec call", "exec('print(123)')"),
    ("create file", "__import__('os').popen('touch /tmp/hacked').read()"),
    ("subclasses", "().__class__.__bases__[0].__subclasses__()"),
    ("socket connection", "__import__('socket').socket().connect(('example.com', 80))"),
    ("lambda trick", "(lambda f: f('ls'))(__import__('os').system)")
]


@pytest.mark.parametrize("description, input_str", EVAL_DANGEROUS_INPUTS)
def test_evaluate_malicious_code(description: str, input_str: str)-> None:
    expected = input_str
    result = evaluate_terraform(input_str)
    assert result == expected
    asteval = get_asteval()
    asteval(input_str)
    assert asteval.error