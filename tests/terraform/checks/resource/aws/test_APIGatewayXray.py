import unittest

from checkov.terraform.checks.resource.aws.APIGatewayXray import check
from checkov.common.models.enums import CheckResult


class TestAPIGatewayXray(unittest.TestCase):

    def test_failure(self):
        resource_conf = {"xray_tracing_enabled": [False]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


    def test_success(self):
        resource_conf = {"xray_tracing_enabled": [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
