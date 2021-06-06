import unittest

import hcl2

from checkov.terraform.checks.data.aws.StarActionPolicyDocument import check
from checkov.common.models.enums import CheckResult


class TestStarActionPolicyDocument(unittest.TestCase):

    def test_success(self):
        resource_conf = {
            "statement": [{
                "actions": [["s3:*"]],
                "resources": [["arn:aws:s3:::my_corporate_bucket/*"]],
                "effect": ["Allow"]
            }]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unknown(self):
        resource_conf = {'statement': [[{'actions': ['s3:GetObject'], 'principals': {'identifiers': ['*'], 'type': 'AWS'}, 'resources': ['aws_s3_bucket.default.arn/*']}], 'flatten(data.aws_iam_policy_document.deployment.*.statement)', 'flatten(data.aws_iam_policy_document.replication.*.statement)']}

        scan_result = check.scan_data_conf(resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {
            "statement": [{
                "actions": [["*"]],
                "resources": [["arn:aws:s3:::my_corporate_bucket/*"]],
                "effect": ["Allow"]
            }]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_effect(self):
        resource_conf = {
            "statement": [{
                "actions": [["*"]],
                "resources": [["arn:aws:s3:::my_corporate_bucket/*"]]
            }]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_flatten_operator(self):
        conf = hcl2.loads("""
        data "aws_iam_policy_document" "mock_policy" {
            statement = flatten(var.policy_json, [])
        }
        """)

        scan_result = check.scan_data_conf(conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
