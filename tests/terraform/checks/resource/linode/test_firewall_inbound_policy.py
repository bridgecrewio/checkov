import unittest

import hcl2
from checkov.terraform.checks.resource.linode.firewall_inbound_policy import check
from checkov.common.models.enums import CheckResult


class Testfirewall_inbound_policy(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "linode_firewall" "test" {
            inbound_policy="DROP"
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_firewall']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "linode_firewall" "test" {
            inbound_policy="ACCEPT"
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_firewall']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
