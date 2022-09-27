import unittest

import hcl2
from checkov.terraform.checks.resource.ncp.LBTargetGroupDefinesHealthCheck import check
from checkov.common.models.enums import CheckResult


class TestLBTargetGroupDefinesHealthCheck(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "ncloud_lb_target_group" "pass" {
              vpc_no   = ncloud_vpc.main.vpc_no
              protocol = "HTTP"
              target_type = "VSVR"
              port        = 8080
              description = "for test"
              health_check {
                protocol = "HTTP"
                http_method = "GET"
                port           = 8080
                url_path       = "/monitor/l7check"
                cycle          = 30
                up_threshold   = 2
                down_threshold = 2
              }
              algorithm_type = "RR"
            }
        """)
        resource_conf = hcl_res['resource'][0]['ncloud_lb_target_group']['pass']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "ncloud_lb_target_group" "fail" {
              vpc_no   = ncloud_vpc.main.vpc_no
              protocol = "HTTP"
              target_type = "VSVR"
              port        = 8080
              description = "for test"
              algorithm_type = "RR"
            }
        """)
        resource_conf = hcl_res['resource'][0]['ncloud_lb_target_group']['fail']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
