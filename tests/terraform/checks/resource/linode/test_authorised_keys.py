import unittest

import hcl2
from checkov.terraform.checks.resource.linode.authorized_keys import check
from checkov.common.models.enums import CheckResult


class Testauthorized_keys(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "linode_instance" "test" {
        authorized_keys="1234355-12345-12-1213123"
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "linode_instance" "test" {
        }
        """)
        resource_conf = hcl_res['resource'][0]['linode_instance']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
