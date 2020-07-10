import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleProjectDefaultNetwork import check
from checkov.common.models.enums import CheckResult


class TestGoogleProjectDefaultNetwork(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "google_project" "my_project" {
                  name       = "My Project"
                  project_id = "your-project-id"
                  org_id     = "1234567"
                }
                """)
        resource_conf = hcl_res['resource'][0]['google_project']['my_project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                        resource "google_project" "my_project" {
                          name       = "My Project"
                          project_id = "your-project-id"
                          org_id     = "1234567"
                          auto_create_network   = false
                        }
                        """)
        resource_conf = hcl_res['resource'][0]['google_project']['my_project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
