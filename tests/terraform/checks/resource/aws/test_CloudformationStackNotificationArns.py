import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.CloudformationStackNotificationArns import check


class TestCloudformationStackNotificationArns(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_cloudformation_stack" "default" {
                  name = "networking-stack"
                
                  parameters = {
                    VPCCidr = "10.0.0.0/16"
                  }
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_cloudformation_stack']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_cloudformation_stack" "default" {
                  name = "networking-stack"
                
                  parameters = {
                    VPCCidr = "10.0.0.0/16"
                  }
                  notification_arns = ["arn1", "arn2"]
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_cloudformation_stack']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
