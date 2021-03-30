import unittest

import hcl2

from checkov.terraform.checks.resource.aws.ELBCrossZoneEnable import check
from checkov.common.models.enums import CheckResult


class TestELBCrossZoneEnable(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_elb" "test_failed" {
              name               = "foobar-terraform-elb"
              availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
            
              access_logs {
                bucket        = "foo"
                bucket_prefix = "bar"
                interval      = 60
              }
            
              listener {
                instance_port     = 8000
                instance_protocol = "http"
                lb_port           = 80
                lb_protocol       = "http"
              }
            
              listener {
                instance_port      = 8000
                instance_protocol  = "http"
                lb_port            = 443
                lb_protocol        = "https"
                ssl_certificate_id = "arn:aws:iam::123456789012:server-certificate/certName"
              }
            
              health_check {
                healthy_threshold   = 2
                unhealthy_threshold = 2
                timeout             = 3
                target              = "HTTP:8000/"
                interval            = 30
              }
            
              instances                   = [aws_instance.foo.id]
              idle_timeout                = 400
              connection_draining         = true
              connection_draining_timeout = 400
            
              cross_zone_load_balancing = false
            }
            """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test_failed']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_missing_attribute(self):
        hcl_res = hcl2.loads("""
            resource "aws_elb" "test_success" {
              name               = "foobar-terraform-elb"
              availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

              access_logs {
                bucket        = "foo"
                bucket_prefix = "bar"
                interval      = 60
              }

              listener {
                instance_port     = 8000
                instance_protocol = "http"
                lb_port           = 80
                lb_protocol       = "http"
              }

              listener {
                instance_port      = 8000
                instance_protocol  = "http"
                lb_port            = 443
                lb_protocol        = "https"
                ssl_certificate_id = "arn:aws:iam::123456789012:server-certificate/certName"
              }

              health_check {
                healthy_threshold   = 2
                unhealthy_threshold = 2
                timeout             = 3
                target              = "HTTP:8000/"
                interval            = 30
              }

              instances                   = [aws_instance.foo.id]
              idle_timeout                = 400
              connection_draining         = true
              connection_draining_timeout = 400
            }
            """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test_success']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "aws_elb" "test_success" {
              name               = "foobar-terraform-elb"
              availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

              access_logs {
                bucket        = "foo"
                bucket_prefix = "bar"
                interval      = 60
              }

              listener {
                instance_port     = 8000
                instance_protocol = "http"
                lb_port           = 80
                lb_protocol       = "http"
              }

              listener {
                instance_port      = 8000
                instance_protocol  = "http"
                lb_port            = 443
                lb_protocol        = "https"
                ssl_certificate_id = "arn:aws:iam::123456789012:server-certificate/certName"
              }

              health_check {
                healthy_threshold   = 2
                unhealthy_threshold = 2
                timeout             = 3
                target              = "HTTP:8000/"
                interval            = 30
              }

              instances                   = [aws_instance.foo.id]
              cross_zone_load_balancing   = true
              idle_timeout                = 400
              connection_draining         = true
              connection_draining_timeout = 400
            }
            """)
        resource_conf = hcl_res['resource'][0]['aws_elb']['test_success']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
