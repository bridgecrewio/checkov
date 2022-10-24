import unittest

import hcl2
from checkov.terraform.checks.resource.linode.user_username_set import check
from checkov.common.models.enums import CheckResult


class Testuser_username_set(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "linode_user" "test" {
        username="linode"
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_user']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "linode_user" "test" {
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_user']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
