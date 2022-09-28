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

    def test_failure_acg_rule(self):
        hcl_res = hcl2.loads("""
                            resource "ncloud_access_control_group_rule" "acg-rule-success" {
                                access_control_group_no = ncloud_access_control_group.acg.id

                                inbound {
                                    protocol = "TCP"
                                    ip_block = "0.0.0.0/0"
                                    port_range = "22"
                                    description = "accept 22 port"
                                }
                                inbound {
                                    protocol = "TCP"
                                    ip_block = "0.0.0.0/0"
                                    port_range = "80"
                                    description = "accept 80 port"
                                }
                                outbound {
                                    protocol = "TCP"
                                    ip_block = "0.0.0.0/0"
                                    port_range = "1-65535"
                                    description = "accept 1-65535 port"
                                }
                            }
                """)
        resource_conf = hcl_res['resource'][0]['ncloud_access_control_group_rule']['acg-rule-success']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_acg_rule(self):
        hcl_res = hcl2.loads("""
            resource "ncloud_access_control_group_rule" "acg-rule-failure" {
                access_control_group_no = ncloud_access_control_group.acg.id

                inbound {
                    protocol = "TCP"
                    ip_block = "0.0.0.0/0"
                    port_range = "22"
                }
                inbound {
                    protocol = "TCP"
                    ip_block = "0.0.0.0/0"
                    port_range = "80"
                }
                outbound {
                    protocol = "TCP"
                    ip_block = "0.0.0.0/0"
                    port_range = "1-65535"
                }
            }
        """)
        resource_conf = hcl_res['resource'][0]['ncloud_access_control_group_rule']['acg-rule-failure']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()

