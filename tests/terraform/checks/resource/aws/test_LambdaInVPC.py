import unittest

from checkov.terraform.checks.resource.aws.LambdaInVPC import check
from checkov.common.models.enums import CheckResult

import hcl2


class TestLambdaInVPC(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_lambda_function" "test_lambda" {
              filename      = "lambda_function_payload.zip"
              function_name = "lambda_function_name"
              role          = aws_iam_role.iam_for_lambda.arn
              handler       = "exports.test"

              source_code_hash = filebase64sha256("lambda_function_payload.zip")

              runtime = "nodejs12.x"

              environment {
                variables = {
                  foo = "bar"
                }
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_lambda_function']['test_lambda']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "aws_lambda_function" "test_lambda" {
              filename      = "lambda_function_payload.zip"
              function_name = "lambda_function_name"
              role          = aws_iam_role.iam_for_lambda.arn
              handler       = "exports.test"
              source_code_hash = filebase64sha256("lambda_function_payload.zip")
              runtime = "nodejs12.x"
              vpc_config {
                # Every subnet should be able to reach an EFS mount target in the same Availability Zone. Cross-AZ mounts are not permitted.
                subnet_ids         = [aws_subnet.subnet_for_lambda.id]
                security_group_ids = [aws_security_group.sg_for_lambda.id]
              }
              environment {
                variables = {
                  foo = "bar"
                }
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_lambda_function']['test_lambda']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
