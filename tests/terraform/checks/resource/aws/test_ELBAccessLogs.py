import unittest
import hcl2

from checkov.terraform.checks.resource.aws.ELBAccessLogs import check
from checkov.common.models.enums import CheckResult


class TestELBAccessLogs(unittest.TestCase):

    def test_failure_elb_1(self):
        hcl_res = hcl2.loads("""
          resource "aws_elb" "test" {
            name = "test-lb-tf"
            availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

            listener {
              instance_port     = 8000
              instance_protocol = "http"
              lb_port           = 80
              lb_protocol       = "http"
            }
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_elb_2(self):
        hcl_res = hcl2.loads("""
          resource "aws_elb" "test" {
            name = "test-lb-tf"
            availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

            listener {
              instance_port     = 8000
              instance_protocol = "http"
              lb_port           = 80
              lb_protocol       = "http"
            }

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              enabled = false   
            }
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)           

    def test_success_elb_1(self):
        hcl_res = hcl2.loads("""
        resource "aws_elb" "test" {
            name = "test-lb-tf"
            availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

            listener {
              instance_port     = 8000
              instance_protocol = "http"
              lb_port           = 80
              lb_protocol       = "http"
            }

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              enabled = true
            }
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_elb_2(self):
        hcl_res = hcl2.loads("""
        resource "aws_elb" "test" {
            name = "test-lb-tf"
            availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

            listener {
              instance_port     = 8000
              instance_protocol = "http"
              lb_port           = 80
              lb_protocol       = "http"
            }

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              # The default value for enabled is true              
            }
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)          


if __name__ == '__main__':
    unittest.main()
