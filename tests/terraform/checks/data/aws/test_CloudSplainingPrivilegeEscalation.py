import unittest

import hcl2
from checkov.terraform.checks.data.aws.IAMPrivilegeEscalation import check

from checkov.common.models.enums import CheckResult


class TestcloudsplainingPrivilegeEscalation(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            data "aws_iam_policy_document" "example" {
              statement {
                sid = "1"
                effect = "Allow"

                actions = [
                    "iam:PassRole",
                    "lambda:CreateFunction",
                    "lambda:CreateEventSourceMapping",
                    "dynamodb:CreateTable",
                    "dynamodb:PutItem",
                ]
            
                resources = [
                  "*",
                ]
              }
            }
        """)
        resource_conf = hcl_res['data'][0]['aws_iam_policy_document']['example']
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            data "aws_iam_policy_document" "example" {
              statement {
                sid = "1"
                effect = "Allow"

                actions = [
                    "lambda:CreateFunction",
                    "lambda:CreateEventSourceMapping",
                    "dynamodb:CreateTable",
                ]
            
                resources = [
                  "*",
                ]
              }
            }
        """)
        resource_conf = hcl_res['data'][0]['aws_iam_policy_document']['example']
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
