import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleOrgMemberDefaultServiceAccount import check
from checkov.common.models.enums import CheckResult


class TestGoogleOrgMemberDefaultServiceAccount(unittest.TestCase):

    def test_failure_binding(self):
        hcl_res = hcl2.loads("""
            resource "google_organization_iam_binding" "organization" {
              org_id  = "your-organization-id"
              role    = "roles/editor"
            
              members = [
                "user:jane@example.com",
                "serviceAccount:test-compute@developer.gserviceaccount.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_organization_iam_binding']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_member(self):
        hcl_res = hcl2.loads("""
            resource "google_organization_iam_member" "organization" {
              org_id  = "your-organization-id"
              role    = "roles/editor"
              member  = "serviceAccount:test-compute@developer.gserviceaccount.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_organization_iam_member']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_binding(self):
        hcl_res = hcl2.loads("""
            resource "google_organization_iam_binding" "organization" {
              org_id  = "your-organization-id"
              role    = "roles/editor"
            
              members = [
                "user:jane@example.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_organization_iam_binding']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_member(self):
        hcl_res = hcl2.loads("""
            resource "google_organization_iam_member" "organization" {
              org_id  = "your-organization-id"
              role    = "roles/editor"
              member  = "user:jane@example.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_organization_iam_member']['organization']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)



if __name__ == '__main__':
    unittest.main()
