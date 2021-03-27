import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.EC2PublicIP import check


class TestEC2PublicIP(unittest.TestCase):
    def test_pass_defaults_aws_instance(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_defaults_aws_launch_template(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_launch_template" "test" {
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_launch_template"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_aws_instance(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
                associate_public_ip_address = true
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_aws_launch_template(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_launch_template" "test" {
                network_interfaces {
                    associate_public_ip_address = true
                }
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_launch_template"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_aws_launch_template(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_launch_template" "test" {
                network_interfaces {
                    associate_public_ip_address = false
                }
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_launch_template"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_aws_instance(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
                associate_public_ip_address = false
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
