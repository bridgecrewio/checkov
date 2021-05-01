import unittest
import hcl2

from checkov.terraform.checks.resource.aws.DynamoDBTablesEncrypted import check
from checkov.common.models.enums import CheckResult


class TestELBAccessLogs(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_dynamodb_table" "basic-dynamodb-table" {
              name           = "GameScores"
              billing_mode   = "PROVISIONED"
              read_capacity  = 20
              write_capacity = 20
              hash_key       = "UserId"
              range_key      = "UserId"
            
              attribute {
                name = "UserId"
                type = "S"
              }
           
              server_side_encryption {
                  enabled = false
              }
            } 
        """)
        resource_conf = hcl_res['resource'][0]['aws_dynamodb_table']['basic-dynamodb-table']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "aws_dynamodb_table" "basic-dynamodb-table" {
              name           = "GameScores"
              billing_mode   = "PROVISIONED"
              read_capacity  = 20
              write_capacity = 20
              hash_key       = "UserId"
              range_key      = "UserId"
            
              attribute {
                name = "UserId"
                type = "S"
              }
            } 
        """)
        resource_conf = hcl_res['resource'][0]['aws_dynamodb_table']['basic-dynamodb-table']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "aws_dynamodb_table" "basic-dynamodb-table" {
              name           = "GameScores"
              billing_mode   = "PROVISIONED"
              read_capacity  = 20
              write_capacity = 20
              hash_key       = "UserId"
              range_key      = "UserId"
            
              attribute {
                name = "UserId"
                type = "S"
              }
           
              server_side_encryption {
                  enabled = true
              }
            } 
        """)
        resource_conf = hcl_res['resource'][0]['aws_dynamodb_table']['basic-dynamodb-table']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
