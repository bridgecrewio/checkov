import os
import unittest

from checkov.serverless.parsers.parser import process_variables, SELF_VAR_PATTERN


IRRELEVANT_DIR = os.curdir

class TestParser(unittest.TestCase):

    def test_ungreedy_match(self):
        count = 0
        for m in SELF_VAR_PATTERN.finditer("${self:source.nested1} - "
                                           "${self:source.more_nesting.nested2} - "
                                           "${self:bogus,aDefault}"):
            print(m[0])
            count += 1
        self.assertEqual(3, count)

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


if __name__ == '__main__':
    unittest.main()
