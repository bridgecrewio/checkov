import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleFolderMemberDefaultServiceAccount import check
from checkov.common.models.enums import CheckResult


class TestGoogleFolderMemberDefaultServiceAccount(unittest.TestCase):

    def test_failure_binding(self):
        hcl_res = hcl2.loads("""
            resource "google_folder_iam_binding" "folder" {
              folder  = "folders/1234567"
              role    = "roles/editor"
            
              members = [
                "user:jane@example.com",
                "serviceAccount:test-compute@appspot.gserviceaccount.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_folder_iam_binding']['folder']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_member(self):
        hcl_res = hcl2.loads("""
            resource "google_folder_iam_member" "folder" {
              folder  = "folders/1234567"
              role    = "roles/editor"
              member  = "serviceAccount:test-compute@developer.gserviceaccount.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_folder_iam_member']['folder']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_binding(self):
        hcl_res = hcl2.loads("""
            resource "google_folder_iam_binding" "folder" {
              folder  = "folders/1234567"
              role    = "roles/editor"
            
              members = [
                "user:jane@example.com",
              ]
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_folder_iam_binding']['folder']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_member(self):
        hcl_res = hcl2.loads("""
            resource "google_folder_iam_member" "folder" {
              folder  = "folders/1234567"
              role    = "roles/editor"
              member  = "user:jane@example.com"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_folder_iam_member']['folder']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)



if __name__ == '__main__':
    unittest.main()
