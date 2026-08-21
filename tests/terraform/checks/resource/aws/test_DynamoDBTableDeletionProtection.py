import unittest

import hcl2

from checkov.terraform.checks.resource.aws.DynamoDBTableDeletionProtection import check
from checkov.common.models.enums import CheckResult


class TestDynamoDBTableDeletionProtection(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_dynamodb_table" "pass" {
                    name           = "GameScores"
                    billing_mode   = "PAY_PER_REQUEST"
                    hash_key       = "UserId"
                    range_key      = "GameTitle"
                    deletion_protection_enabled = true

                    attribute {
                        name = "UserId"
                        type = "S"
                    }

                    attribute {
                        name = "GameTitle"
                        type = "S"
                    }
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_dynamodb_table']['pass']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_dynamodb_table" "fail" {
                    name           = "GameScores"
                    billing_mode   = "PAY_PER_REQUEST"
                    hash_key       = "UserId"
                    range_key      = "GameTitle"
                    deletion_protection_enabled = false

                    attribute {
                        name = "UserId"
                        type = "S"
                    }

                    attribute {
                        name = "GameTitle"
                        type = "S"
                    }
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_dynamodb_table']['fail']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_missing_attribute(self):
        hcl_res = hcl2.loads("""
                resource "aws_dynamodb_table" "fail_missing" {
                    name           = "GameScores"
                    billing_mode   = "PAY_PER_REQUEST"
                    hash_key       = "UserId"
                    range_key      = "GameTitle"

                    attribute {
                        name = "UserId"
                        type = "S"
                    }

                    attribute {
                        name = "GameTitle"
                        type = "S"
                    }
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_dynamodb_table']['fail_missing']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
