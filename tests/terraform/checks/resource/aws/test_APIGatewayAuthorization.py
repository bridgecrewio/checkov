import unittest

from checkov.terraform.checks.resource.aws.APIGatewayAuthorization import check
from checkov.common.models.enums import CheckResult


class TestAPIGatewayAuthorization(unittest.TestCase):

    def test_failure(self):
        resource_conf = {"rest_api_id": ["${var.rest_api_id}"],
                         "resource_id": ["${var.resource_id}"],
                         "http_method": ["${var.method}"],
                         "authorization": ["NONE"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"rest_api_id": ["${var.rest_api_id}"],
                         "resource_id": ["${var.resource_id}"],
                         "http_method": ["${var.method}"],
                         "authorization": ["AWS_IAM"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_apikey(self):
        resource_conf = {"rest_api_id": ["${var.rest_api_id}"],
                         "resource_id": ["${var.resource_id}"],
                         "http_method": ["${var.method}"],
                         "authorization": ["NONE"],
                         "api_key_required": [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_authorization_missing(self):
        resource_conf = {"rest_api_id": ["${var.rest_api_id}"],
                         "resource_id": ["${var.resource_id}"],
                         "http_method": ["${var.method}"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
