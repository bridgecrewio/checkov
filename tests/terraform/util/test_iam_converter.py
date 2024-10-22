import unittest

from checkov.terraform.checks.utils.iam_terraform_document_to_policy_converter import (
    convert_terraform_conf_to_iam_policy,
)


class TestIAMConverter(unittest.TestCase):
    def test_iam_converter(self):
        conf = {'version': ['2012-10-17'], 'statement': [{'actions': [['*']], 'resources': [['*']]}]}
        expected_result = {'version': ['2012-10-17'], 'Statement': [{'Action': ['*'], 'Resource': ['*'], 'Effect': 'Allow'}]}
        result = convert_terraform_conf_to_iam_policy(conf)
        self.assertDictEqual(result, expected_result)
        self.assertNotEqual(result, conf)

    def test_convert_condition(self):
        # given
        conf = {
            "__end_line__": 77,
            "__start_line__": 42,
            "statement": [
                {
                    "actions": [["kms:Decrypt", "kms:GenerateDataKey"]],
                    "condition": [
                        {
                            "test": ["ForAnyValue:StringEquals"],
                            "values": [["pi"]],
                            "variable": ["kms:EncryptionContext:service"],
                        },
                        {
                            "test": ["ForAnyValue:StringEquals"],
                            "values": [["rds"]],
                            "variable": ["kms:EncryptionContext:aws:pi:service"],
                        },
                        {
                            "test": ["ForAnyValue:StringEquals"],
                            "values": [["db-AAAAABBBBBCCCCCDDDDDEEEEE", "db-EEEEEDDDDDCCCCCBBBBBAAAAA"]],
                            "variable": ["kms:EncryptionContext:aws:rds:db-id"],
                        },
                        {"test": ["ArnEquals"], "values": [["arn"]], "variable": ["aws:SourceArn"]},
                    ],
                    "resources": [["*"]],
                }
            ],
            "__address__": "aws_iam_policy_document.example_multiple_condition_keys_and_values",
        }

        result = convert_terraform_conf_to_iam_policy(conf)

        self.assertDictEqual(
            result,
            {
                "__end_line__": 77,
                "__start_line__": 42,
                "__address__": "aws_iam_policy_document.example_multiple_condition_keys_and_values",
                "Statement": [
                    {
                        "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
                        "Resource": ["*"],
                        "Effect": "Allow",
                        "Condition": {
                            "ForAnyValue:StringEquals": {
                                "kms:EncryptionContext:service": ["pi"],
                                "kms:EncryptionContext:aws:pi:service": ["rds"],
                                "kms:EncryptionContext:aws:rds:db-id": [
                                    "db-AAAAABBBBBCCCCCDDDDDEEEEE",
                                    "db-EEEEEDDDDDCCCCCBBBBBAAAAA",
                                ],
                            },
                            "ArnEquals": {"aws:SourceArn": ["arn"]},
                        },
                    }
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
