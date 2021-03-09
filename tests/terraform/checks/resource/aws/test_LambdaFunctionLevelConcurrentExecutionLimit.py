import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.LambdaFunctionLevelConcurrentExecutionLimit import check
import hcl2


class TestLambdaFunctionLevelConcurrentExecutionLimit(unittest.TestCase):

    def test_failure1(self):
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

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "aws_lambda_function" "test_lambda" {
              filename      = "lambda_function_payload.zip"
              function_name = "lambda_function_name"
              role          = aws_iam_role.iam_for_lambda.arn
              handler       = "exports.test"

              source_code_hash = filebase64sha256("lambda_function_payload.zip")
              reserved_concurrent_executions = -1

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

    def test_success1(self):
        hcl_res = hcl2.loads("""
        resource "aws_lambda_function" "test_lambda" {
              filename      = "lambda_function_payload.zip"
              function_name = "lambda_function_name"
              role          = aws_iam_role.iam_for_lambda.arn
              handler       = "exports.test"

              source_code_hash = filebase64sha256("lambda_function_payload.zip")
              reserved_concurrent_executions = 0

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
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
        resource "aws_lambda_function" "test_lambda" {
              filename      = "lambda_function_payload.zip"
              function_name = "lambda_function_name"
              role          = aws_iam_role.iam_for_lambda.arn
              handler       = "exports.test"

              source_code_hash = filebase64sha256("lambda_function_payload.zip")
              reserved_concurrent_executions = 1000

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
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
