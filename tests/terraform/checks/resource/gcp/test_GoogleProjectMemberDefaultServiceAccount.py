import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleProjectMemberDefaultServiceAccount import check
from checkov.common.models.enums import CheckResult


class TestGoogleProjectMemberDefaultServiceAccount(unittest.TestCase):

    def test_failure_binding(self):
        hcl_res = hcl2.loads("""
            resource "google_project_iam_binding" "project" {
              project = "your-project-id"
              role    = "roles/editor"
            
              members = [
                "user",
                "serviceAccount:test-compute@developer.gserviceaccount.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_binding']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_member(self):
        hcl_res = hcl2.loads("""
            resource "google_project_iam_member" "project" {
              project = "your-project-id"
              role    = "roles/editor"
              member  = "serviceAccount:test-compute@developer.gserviceaccount.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_member']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_binding(self):
        hcl_res = hcl2.loads("""
            resource "google_project_iam_binding" "project" {
              project = "your-project-id"
              role    = "roles/editor"
            
              members = [
                "user@mail.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_binding']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_member(self):
        hcl_res = hcl2.loads("""
            resource "google_project_iam_member" "project" {
              project = "your-project-id"
              role    = "roles/editor"
              member  = "user@mail.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_project_iam_member']['project']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)



if __name__ == '__main__':
    unittest.main()
