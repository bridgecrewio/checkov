import unittest

import hcl2

from checkov.terraform.checks.resource.aws.LambdaCodeSigningConfigured import check
from checkov.common.models.enums import CheckResult


class TestLambdaCodeSigningConfigured(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                        resource "aws_lambda_function" "fail" {
                          function_name = "stest-env"
                          role          = ""
                          runtime       = "python3.8"
                        }
                        """)
        resource_conf = hcl_res['resource'][0]['aws_lambda_function']['fail']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_lambda_function" "pass" {
                      function_name = "test-env"
                      role          = ""
                      runtime       = "python3.8"
                      code_signing_config_arn = "123123123"
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['aws_lambda_function']['pass']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
