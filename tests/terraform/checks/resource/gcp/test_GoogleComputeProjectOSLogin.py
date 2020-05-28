import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeProjectOSLogin import check
from checkov.common.models.enums import CheckResult


class TestGoogleComputeProjectOSLogin(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_project_metadata" "default" {
              metadata = {
                foo  = "bar"
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_project_metadata']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "google_compute_project_metadata" "default" {
                      metadata = {
                        foo  = "bar"
                        enable-oslogin = true
                      }
                    }
                        """)
        resource_conf = hcl_res['resource'][0]['google_compute_project_metadata']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
