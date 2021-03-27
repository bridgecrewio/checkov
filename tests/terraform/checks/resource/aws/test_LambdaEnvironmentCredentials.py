import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.LambdaEnvironmentCredentials import check


class TestLambdaCredentials(unittest.TestCase):
    def test_success(self):
        conf = {
            "filename": ["resources/lambda_function_payload.zip"],
            "function_name": ["${local.resource_prefix.value}-analysis"],
            "role": ["${aws_iam_role.iam_for_lambda.arn}"],
            "handler": ["exports.test"],
            "source_code_hash": [
                '${filebase64sha256("resources/lambda_function_payload.zip")}'
            ],
            "runtime": ["nodejs12.x"],
            "environment": [{"variables": [{"foo": "bar"}]}],
        }

        scan_result = check.scan_resource_conf(conf=conf)
        self.assertEqual(CheckResult.PASSED, scan_result)
        conf = {
            "filename": ["resources/lambda_function_payload.zip"],
            "function_name": ["${local.resource_prefix.value}-analysis"],
            "role": ["${aws_iam_role.iam_for_lambda.arn}"],
            "handler": ["exports.test"],
            "source_code_hash": [
                '${filebase64sha256("resources/lambda_function_payload.zip")}'
            ],
            "runtime": ["nodejs12.x"],
        }
        scan_result = check.scan_resource_conf(conf=conf)

        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        conf = {
            "filename": ["resources/lambda_function_payload.zip"],
            "function_name": ["${local.resource_prefix.value}-analysis"],
            "role": ["${aws_iam_role.iam_for_lambda.arn}"],
            "handler": ["exports.test"],
            "source_code_hash": [
                '${filebase64sha256("resources/lambda_function_payload.zip")}'
            ],
            "runtime": ["nodejs12.x"],
            "environment": [
                {
                    "variables": [
                        {
                            "access_key": "AKIAIOSFODNN7EXAMPLE",
                            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                        }
                    ]
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
