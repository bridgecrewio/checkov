import unittest

import hcl2

from checkov.terraform.checks.resource.aws.LBDeletionProtection import check
from checkov.common.models.enums import CheckResult


class TestLBDeletionProtection(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_lb" "test_failed" {
                    name               = "test-lb-tf"
                    internal           = false
                    load_balancer_type = "network"
                    subnets            = aws_subnet.public.*.id
                    enable_deletion_protection = false
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_lb']['test_failed']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_missing_attribute(self):
        hcl_res = hcl2.loads("""
                   resource "aws_lb" "test_failed" {
                       name               = "test-lb-tf"
                       internal           = false
                       load_balancer_type = "network"
                       subnets            = aws_subnet.public.*.id
                   }
                   """)
        resource_conf = hcl_res['resource'][0]['aws_lb']['test_failed']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
               resource "aws_lb" "test_success" {
                    name               = "test-lb-tf"
                    internal           = false
                    load_balancer_type = "network"
                    subnets            = aws_subnet.public.*.id
                    enable_deletion_protection = true
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_lb']['test_success']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
