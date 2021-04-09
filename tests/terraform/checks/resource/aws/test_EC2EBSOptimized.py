import unittest
import hcl2

from checkov.terraform.checks.resource.aws.EC2EBSOptimized import check
from checkov.common.models.enums import CheckResult


class TestEC2EBSOptimized(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_instance" "foo" {
              subnet_id   = some_id
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_instance']['foo']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_default(self):
        hcl_res = hcl2.loads("""
            resource "aws_instance" "foo" {
              subnet_id     = some_id
              ebs_optimized = true
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_instance']['foo']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
