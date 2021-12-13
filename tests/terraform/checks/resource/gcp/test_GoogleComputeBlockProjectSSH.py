import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GoogleComputeBlockProjectSSH import check
from checkov.common.models.enums import CheckResult


class TestGoogleComputeBlockProjectSSH(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              metadata = {
                 block-project-ssh-keys = true
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_instance_template_failure(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_template" "default_template" {
              name         = "test"
              machine_type = "e2-medium"
            
              disk {
                source_image = "debian-cloud/debian-9"
                auto_delete  = true
                disk_size_gb = 100
                boot         = true
              }
            
              network_interface {
                network = "default"
              }
            
              metadata = {
                foo = "bar"
              }
            
              can_ip_forward = true
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_template']['default_template']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_instance_template_success(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_template" "default_template" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
                              
              disk {
                source_image = "debian-cloud/debian-9"
                auto_delete  = true
                disk_size_gb = 100
                boot         = true
              }
            
              network_interface {
                network = "default"
              }
              
              can_ip_forward = true
              metadata = {
                foo                    = "bar",
                block-project-ssh-keys = true
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_template']['default_template']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_no_from_template_support(self):
        if 'google_compute_instance_from_template' in check.supported_resources:
            self.fail("This policy should not support 'google_compute_instance_from_template' resources since it isn't "
                      "possible to scan values inherited from the 'source_instance_template'.")


if __name__ == '__main__':
    unittest.main()
