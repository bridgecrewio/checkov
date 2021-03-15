import unittest
import hcl2

from checkov.terraform.checks.resource.aws.SubnetPublicIP import check
from checkov.common.models.enums import CheckResult


class TestSubnetPublicIP(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                            resource "aws_subnet" "test" {
                              vpc_id     = aws_vpc.main.id
                              cidr_block = "10.0.1.0/24"

                              map_public_ip_on_launch = true
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_subnet']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                            resource "aws_subnet" "test" {
                              vpc_id     = aws_vpc.main.id
                              cidr_block = "10.0.1.0/24"
                              
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_subnet']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_implicit(self):
        hcl_res = hcl2.loads("""
                            resource "aws_subnet" "test" {
                              vpc_id     = aws_vpc.main.id
                              cidr_block = "10.0.1.0/24"
                            
                              map_public_ip_on_launch = false
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_subnet']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
