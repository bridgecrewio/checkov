import unittest

import hcl2
from checkov.terraform.checks.resource.github.PrivateRepo import check
from checkov.common.models.enums import CheckResult


class TestPrivateRepo(unittest.TestCase):

    def test_success_private_true(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "test" {
            description   = "test repo"
            name          = "test"
            private       = true
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_visibility_private(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "test" {
            description   = "test repo"
            name          = "test"
            visibility    = "private"
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_visibility_internal(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "test" {
            description   = "test repo"
            name          = "test"
            visibility    = "internal"
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_private_false(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "test" {
            description   = "test repo"
            name          = "test"
            private       = false
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_default(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "test" {
            description   = "test repo"
            name          = "test"
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_visibility_public(self):
        hcl_res = hcl2.loads("""
        resource "github_repository" "test" {
            description   = "test repo"
            name          = "test"
            visibility    = "public"
        }
        """)
        resource_conf = hcl_res['resource'][0]['github_repository']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
