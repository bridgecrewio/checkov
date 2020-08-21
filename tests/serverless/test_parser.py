import unittest

from checkov.serverless.parsers.parser import process_self_variables, SELF_VAR_PATTERN


class TestParser(unittest.TestCase):

    def test_ungreedy_match(self):
        count = 0
        for m in SELF_VAR_PATTERN.finditer("${self:source.nested1} - "
                                           "${self:source.more_nesting.nested2} - "
                                           "${self:bogus,aDefault}"):
            print(m[0])
            count += 1
        self.assertEqual(3, count)

    def test_process_self_variables(self):
        cases = [
            # Input, Expected
            (
                {
                    "source": "var-data",
                    "consumer": "${self:source}"
                },
                {
                    "source": "var-data",
                    "consumer": "var-data"
                }
            ),
            (
                {
                    "consumer": "${self:source-of-var-data,aDefaultValue}"
                },
                {
                    "consumer": "aDefaultValue"
                }
            ),
            (
                {
                    "source": {
                        "nested1": "value one",
                        "more_nesting": {
                            "nested2": "value two"
                        }
                    },
                    "consumer": "${self:source.nested1} - ${self:source.more_nesting.nested2} - ${self:bogus,aDefault}"
                },
                {
                    "source": {
                        "nested1": "value one",
                        "more_nesting": {
                            "nested2": "value two"
                        }
                    },
                    "consumer": "value one - value two - aDefault"
                }
            ),
            (
                {
                    "consumer": "${self:bogus-no-default}"
                },
                {
                    "consumer": ""
                }
            ),
            (
                {
                    "source": "var-data",
                    "consumer-list": [
                        {
                            "consumer": "${self:source}"
                        }
                    ]
                },
                {
                    "source": "var-data",
                    "consumer-list": [
                        {
                            "consumer": "var-data"
                        }
                    ]
                },
            ),
            (
                {
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
                                    'Resource': ['arn:aws:lambda:#{AWS::Region}:#{AWS::AccountId}:function:invokedLambda'],
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
                },
                {
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
                                    'Resource': ['arn:aws:lambda:#{AWS::Region}:#{AWS::AccountId}:function:invokedLambda'],
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
                },
            )
        ]
        for case in cases:
            result = case[0]
            process_self_variables(result)
            self.assertEqual(case[1], result)


if __name__ == '__main__':
    unittest.main()
