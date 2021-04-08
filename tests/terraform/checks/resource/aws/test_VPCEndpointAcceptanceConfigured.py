import unittest
import hcl2

from checkov.terraform.checks.resource.aws.VPCEndpointAcceptanceConfigured import check
from checkov.common.models.enums import CheckResult


class TestVPCEndpointAcceptanceConfigured(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_vpc_endpoint_service" "example" {
                  acceptance_required        = false
                  network_load_balancer_arns = [aws_lb.example.arn]
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_vpc_endpoint_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_vpc_endpoint_service" "example" {
                  acceptance_required        = true
                  network_load_balancer_arns = [aws_lb.example.arn]
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_vpc_endpoint_service']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
