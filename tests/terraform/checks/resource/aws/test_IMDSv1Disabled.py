import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.IMDSv1Disabled import check


class TestIMDSv1Disabled(unittest.TestCase):
    def test_failure_defaults(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
              metadata_options {
              }
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_optional_tokens(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
              metadata_options {
                http_endpoint               = "enabled"
                http_put_response_hop_limit = "1"
                http_tokens                 = "optional"
              }
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_disabled(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
              metadata_options {
                http_endpoint               = "disabled"
              }
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_enabled_and_tokens_required(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_instance" "test" {
              metadata_options {
                http_endpoint               = "enabled"
                http_tokens                 = "required"
              }
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_instance"]["test"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
