import os
import unittest

from checkov.serverless.parsers.parser \
    import process_variables, _tokenize_by_commas, _token_to_type_and_loc, _parse_var


IRRELEVANT_DIR = os.curdir

class TestParser(unittest.TestCase):

    #########################################
    # "Self" variable processing

    def test_self_simple(self):
        case = {
            "source": "var-data",
            "consumer": "${self:source}"
        }
        expected = {
            "source": "var-data",
            "consumer": "var-data"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_with_default(self):
        case = {
            "consumer": "${self:source-of-var-data,aDefaultValue}"
        }
        expected = {
            "consumer": "aDefaultValue"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_nexted(self):
        case = {
            "source": {
                "nested1": "value one",
                "more_nesting": {
                    "nested2": "value two"
                }
            },
            "consumer": "${self:source.nested1} - ${self:source.more_nesting.nested2} - ${self:bogus,aDefault}"
        }
        expected = {
            "source": {
                "nested1": "value one",
                "more_nesting": {
                    "nested2": "value two"
                }
            },
            "consumer": "value one - value two - aDefault"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_invalid(self):
        case = {
            "consumer": "${self:bogus-no-default}"
        }
        expected = {
            "consumer": "${self:bogus-no-default}"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_list(self):
        case = {
            "source": "var-data",
            "consumer-list": [
                {
                    "consumer": "${self:source}"
                }
            ]
        }
        expected = {
            "source": "var-data",
            "consumer-list": [
                {
                    "consumer": "var-data"
                }
            ]
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_real_world_data(self):
        case = {
            'service': 'my-sls-service',
            'custom': {
                'my_sneaky_custom_var': '*',
                '__startline__': 4,
                '__endline__': 6
            },
            'provider': {
                'name': 'aws',
                'runtime': 'python3.7',
                'stackName': 'lambda-',
                'tag': '${opt:tag}',
                'iamRoleStatements': [
                    {
                        'Effect': 'Allow',
                        'Action': '${self:custom.my_sneaky_custom_var}',
                        'Resource': '${self:custom.my_sneaky_custom_var}',
                        '__startline__': 13,
                        '__endline__': 17
                    }
                ],
                '__startline__': 7,
                '__endline__': 17
            },
            'functions': {
                'myFunc': {
                    'name': 'myFunc-provider-level-with-var',
                    'tags': {
                        'RESOURCE': 'lambda',
                        'PUBLIC': False,
                        '__startline__': 21,
                        '__endline__': 23
                    },
                    'iamRoleStatements': [
                        {
                            'Effect': 'Allow',
                            'Action': ['lambda:InvokeFunction'],
                            'Resource': [
                                'arn:aws:lambda:#{AWS::Region}:#{AWS::AccountId}:function:invokedLambda'],
                            '__startline__': 24,
                            '__endline__': 29
                        }
                    ],
                    'handler': 'Handler.handle',
                    'timeout': 600,
                    'memorySize': 320,
                    '__startline__': 19,
                    '__endline__': 31
                },
                '__startline__': 18,
                '__endline__': 31
            },
            '__startline__': 1,
            '__endline__': 31
        }
        expected = {
            'service': 'my-sls-service',
            'custom': {
                'my_sneaky_custom_var': '*',
                '__startline__': 4,
                '__endline__': 6
            },
            'provider': {
                'name': 'aws',
                'runtime': 'python3.7',
                'stackName': 'lambda-',
                'tag': '${opt:tag}',
                'iamRoleStatements': [
                    {
                        'Effect': 'Allow',
                        'Action': '*',
                        'Resource': '*',
                        '__startline__': 13,
                        '__endline__': 17
                    }
                ],
                '__startline__': 7,
                '__endline__': 17
            },
            'functions': {
                'myFunc': {
                    'name': 'myFunc-provider-level-with-var',
                    'tags': {
                        'RESOURCE': 'lambda',
                        'PUBLIC': False,
                        '__startline__': 21,
                        '__endline__': 23
                    },
                    'iamRoleStatements': [
                        {
                            'Effect': 'Allow',
                            'Action': ['lambda:InvokeFunction'],
                            'Resource': [
                                'arn:aws:lambda:#{AWS::Region}:#{AWS::AccountId}:function:invokedLambda'],
                            '__startline__': 24,
                            '__endline__': 29
                        }
                    ],
                    'handler': 'Handler.handle',
                    'timeout': 600,
                    'memorySize': 320,
                    '__startline__': 19,
                    '__endline__': 31
                },
                '__startline__': 18,
                '__endline__': 31
            },
            '__startline__': 1,
            '__endline__': 31
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_indirection(self):
        case = {
            "consumer": "${self:custom.forward} ${self:custom.four}",
            "custom": {
                "four": "4",
                "two": "2",
                "one": "1",
                "forward": "${self:custom.one} ${self:custom.two} ${self:custom.three}",
                "three": "${self:custom.tres}",
                "tres": "3"
            }
        }
        expected = {
            "consumer": "1 2 3 4",
            "custom": {
                "four": "4",
                "two": "2",
                "one": "1",
                "forward": "1 2 3",
                "three": "3",
                "tres": "3"
            }
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_self_circular_ref(self):
        case = {
            "custom": {
                "thing1": "${self:custom.thing2}",
                "thing2": "${self:custom.thing1}"
            }
        }
        result = process_variables(case, IRRELEVANT_DIR)
        # Undefined which will be picked, but won't be fully resolved
        self.assertTrue(result["custom"]["thing1"].startswith("${self:custom.thing"))
        self.assertTrue(result["custom"]["thing2"].startswith("${self:custom.thing"))

    def test_self_reference(self):
        case = {
            "me": "${self:me}"
        }
        expected = {
            "me": "${self:me}"
        }
        # Should just finish, no hang, no changes
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_nested(self):
        case = {
            "second-value": "final",
            "first-value": "second",
            "consumer": "${self:${self:first-value}-value}"
        }
        expected = {
            "second-value": "final",
            "first-value": "second",
            "consumer": "final"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_overwriting_variables(self):
        case = {
            "fallback": "final",
            "value": "${self:doesnt-exist, self:fallback}"
        }
        expected = {
            "fallback": "final",
            "value": "final"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_custom_variable_syntax(self):
        case = {
            "provider": {
                "variableSyntax": "\\${{([ ~:a-zA-Z0-9._@\\'\",\\-\\/\\(\\)]+?)}}"
            },
            "custom": {
                "consumer": "${{self: custom.source}}",
                "source": "final"
            }
        }
        expected = {
            # NOTE: variableSyntax entry is removed to prevent self-matching
            "provider": {},
            "custom": {
                "consumer": "final",
                "source": "final"
            }
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_deep_var_override(self):
        case = {
            "custom": {
                "val1": "${self:not.a.value, 'bar'}",
                "val2": "${self:custom.val1}"
            }
        }
        expected = {
            "custom": {
                "val1": "bar",
                "val2": "bar"
            }
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_deep_references_into_deep_vars(self):
        case = {
            "custom": {
                "val0": {
                    "foo": "bar"
                },
                "val1": '${self:custom.val0}',
                "val2": '${self:custom.val1.foo}',
            }
        }
        expected = {
            "custom": {
                "val0": {
                    "foo": 'bar',
                },
                "val1": {
                    "foo": 'bar',
                },
                "val2": 'bar',
            }
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_quoted_vars(self):
        case = {
            "consumer": "${self: custom.bogus, \"value, with, commas\"}",
        }
        expected = {
            "consumer": "value, with, commas"
        }
        self.assertEqual(expected, process_variables(case, IRRELEVANT_DIR))

    def test_tokenize_by_commas(self):
        self.assertEqual(["single"],
                         _tokenize_by_commas("single"))
        self.assertEqual(["one", "two"],
                         _tokenize_by_commas("one,two"))
        self.assertEqual(["one", "two"],
                         _tokenize_by_commas("one, two"))
        # Double quotes
        self.assertEqual(["separate", "commas, in, value", "another"],
                         _tokenize_by_commas("separate, \"commas, in, value\", another"))
        self.assertEqual(["commas, in, value", "another"],
                         _tokenize_by_commas("\"commas, in, value\", another"))
        self.assertEqual(["separate", "commas, in, value"],
                         _tokenize_by_commas("separate, \"commas, in, value\""))
        # Single quotes
        self.assertEqual(["separate", "commas, in, value", "another"],
                         _tokenize_by_commas("separate, 'commas, in, value', another"))
        self.assertEqual(["commas, in, value", "another"],
                         _tokenize_by_commas("'commas, in, value', another"))
        self.assertEqual(["separate", "commas, in, value"],
                         _tokenize_by_commas("separate, 'commas, in, value'"))

    def test_token_to_type_and_loc(self):
        self.assertEqual(("self", "foo"),
                         _token_to_type_and_loc("self:foo"))
        self.assertEqual(("self", "foo"),
                         _token_to_type_and_loc("self: foo"))
        self.assertEqual(("something_made_up", "bar"),
                         _token_to_type_and_loc("something_made_up:bar"))
        self.assertEqual(("file(~/settings.yaml)", "foo"),
                         _token_to_type_and_loc("file(~/settings.yaml):foo"))
        self.assertEqual(("file(~/settings.yaml)", None),
                         _token_to_type_and_loc("file(~/settings.yaml)"))

    def test_parse_var(self):
        self.assertEqual(("self", "foo", "self", "bar"),
                         _parse_var("self:foo,self:bar"))
        self.assertEqual(("self", "foo", None, "bar"),
                         _parse_var("self:foo,bar"))
        self.assertEqual(("file(settings.yaml)", "foo", "self", "bar"),
                         _parse_var("file(settings.yaml):foo,self:bar"))
        self.assertEqual(("file(settings.yaml)", "foo", None, None),
                         _parse_var("file(settings.yaml):foo"))
        self.assertEqual(("file(settings.yaml)", None, None, None),
                         _parse_var("file(settings.yaml)"))

        self.assertEqual(("self", "foo", None, None),
                         _parse_var("self: foo"))       # eat whitespace


if __name__ == '__main__':
    unittest.main()
