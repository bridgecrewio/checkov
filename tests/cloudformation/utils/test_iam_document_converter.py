import unittest

from checkov.cloudformation.checks.utils.iam_cloudformation_document_to_policy_converter import (
    convert_cloudformation_conf_to_iam_policy,
)


class TestIamDocumentConverter(unittest.TestCase):
    """IAM grammar allows a PolicyDocument ``Statement`` to be a single object
    instead of a list. The converter must normalize it so downstream analysis
    sees the same shape either way."""

    def test_single_object_statement_normalized_to_list(self):
        statement = {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": "*"}

        result = convert_cloudformation_conf_to_iam_policy({"Statement": statement})

        self.assertIsInstance(result["Statement"], list)
        self.assertEqual(result["Statement"], [statement])

    def test_single_object_and_single_item_list_are_equivalent(self):
        statement = {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": "*"}

        as_object = convert_cloudformation_conf_to_iam_policy({"Statement": statement})
        as_list = convert_cloudformation_conf_to_iam_policy({"Statement": [statement]})

        self.assertEqual(as_object["Statement"], as_list["Statement"])

    def test_list_statement_left_as_list(self):
        statements = [
            {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": "*"},
            {"Effect": "Deny", "Action": ["s3:DeleteObject"], "Resource": "*"},
        ]

        result = convert_cloudformation_conf_to_iam_policy({"Statement": statements})

        self.assertEqual(result["Statement"], statements)


if __name__ == "__main__":
    unittest.main()
