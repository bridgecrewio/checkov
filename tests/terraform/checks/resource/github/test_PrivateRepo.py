import unittest

import hcl2
from checkov.terraform.checks.resource.github.PrivateRepo import check
from checkov.common.models.enums import CheckResult


class TestPrivateRepo(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "example" {
            description   = "examplea code"
            name          = "exampla"
            private       = false
        }

        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "example" {
            description   = "examplea code"
            name          = "exampla"
            private       = true
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
