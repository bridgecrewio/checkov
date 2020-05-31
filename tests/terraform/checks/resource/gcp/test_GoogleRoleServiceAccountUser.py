import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleRoleServiceAccountUser import check
from checkov.common.models.enums import CheckResult


class TestGoogleRoleServiceAccountUser(unittest.TestCase):

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "google_project_iam_member" "project" {
              project = "your-project-id"
              role    = "roles/iam.serviceAccountUser"
              member  = "user:jane@example.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_member']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "google_project_iam_binding" "project" {
              project = "your-project-id"
              role    = "roles/iam.serviceAccountTokenCreator"

              members = [
                "user:jane@example.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_binding']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "google_project_iam_member" "project" {
          project = "your-project-id"
          role    = "roles/editor"
          member  = "user:jane@example.com"
        }
                        """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_member']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
