import unittest
import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.APIGatewayCacheEnable import check


class TestAPIGatewayCacheEnable(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "aws_api_gateway_rest_api" "example" {                    
                      name = "example"
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_api_gateway_rest_api']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_api_gateway_rest_api" "example" {                    
                      name                  = "example"
                      cache_cluster_enabled = true
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_api_gateway_rest_api']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
