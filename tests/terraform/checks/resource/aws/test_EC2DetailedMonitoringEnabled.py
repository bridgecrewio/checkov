import unittest

import hcl2

from checkov.terraform.checks.resource.aws.EC2DetailedMonitoringEnabled import check
from checkov.common.models.enums import CheckResult


class TestEC2PublicIP(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
            resource "aws_instance" "test" {
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "aws_launch_template" "test" {
                monitoring = false
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_launch_template']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_aws_instance(self):
        hcl_res = hcl2.loads("""
            resource "aws_instance" "test" {
                monitoring = true
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
