import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription import check


class TestSecurityGroupRuleDescription(unittest.TestCase):
    
    def test_failure(self):
        hcl_res = hcl2.loads("""
                        resource "ncloud_access_control_group" "acg" {
                            name = "example-acg"
                            vpc_no = data.ncloud_vpc.selected.id
                        }
                """)
        resource_conf = hcl_res['resource'][0]['ncloud_access_control_group']['acg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


    def test_sucess_acg_desc(self):
        hcl_res = hcl2.loads("""
                        resource "ncloud_access_control_group" "acg-success" {
                            name = "example-acg"
                            description = "description"
                            vpc_no = data.ncloud_vpc.selected.id
                        }
                """)
        resource_conf = hcl_res['resource'][0]['ncloud_access_control_group']['acg-success']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
