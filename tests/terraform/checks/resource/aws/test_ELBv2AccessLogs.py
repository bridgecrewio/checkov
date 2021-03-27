import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.ELBv2AccessLogs import check


class TestELBAccessLogs(unittest.TestCase):
    def test_failure_lb_1(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_lb" "test" {
            name               = "test-lb-tf"

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
            }
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_lb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_lb_2(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_lb" "test" {
            name               = "test-lb-tf"

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              enabled = false
            }
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_lb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_lb_3(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_lb" "test" {
            name               = "test-lb-tf"
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_lb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_alb_1(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_alb" "test" {
            name               = "test-lb-tf"

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
            }
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_alb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_alb_2(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_alb" "test" {
            name               = "test-lb-tf"

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              enabled = false
            }
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_alb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_alb_3(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_alb" "test" {
            name               = "test-lb-tf"
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_alb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_lb(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_lb" "test" {
            name               = "test-lb-tf"

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              enabled = true
            }
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_lb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_alb(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_alb" "test" {
            name               = "test-lb-tf"

            access_logs {
              bucket  = aws_s3_bucket.lb_logs.bucket
              enabled = true
            }
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_alb"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
