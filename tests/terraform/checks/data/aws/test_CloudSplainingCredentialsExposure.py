import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.data.aws.IAMCredentialsExposure import check


class TestcloudsplainingPrivilegeEscalation(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            data "aws_iam_policy_document" "example" {
              statement {
                sid = "1"
                effect = "Allow"

                actions = [
                        "s3:GetObject",
                        "iam:CreateAccessKey"
                ]

                resources = [
                  "*",
                ]
              }
            }
        """
        )
        resource_conf = hcl_res["data"][0]["aws_iam_policy_document"]["example"]
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
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
        """
        )
        resource_conf = hcl_res["data"][0]["aws_iam_policy_document"]["example"]
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_deny(self):
        hcl_res = hcl2.loads(
            """
             data "aws_iam_policy_document" "DenyOutsideCallers" {
               statement {
                 sid       = "DenyOutsideCallers"
                 effect    = "Deny"
                 actions   = ["*"]
                 resources = ["*"]

                 condition {
                   test     = "NotIpAddress"
                   variable = "aws:SourceIp"
                   values = [
                     "1.2.3.4/16"
                   ]
                 }

                 condition {
                   test     = "Bool"
                   variable = "aws:ViaAWSService"
                   values   = ["false"]
                 }
               }
             }
        """
        )

        resource_conf = hcl_res["data"][0]["aws_iam_policy_document"][
            "DenyOutsideCallers"
        ]
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
