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

    def test_failure_1(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance" "default" {
              name         = "test"
              machine_type = "n1-standard-1"
              zone         = "us-central1-a"
              metadata = {
                 block-project-ssh-keys = false
              }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_2(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_from_template" "default" {
              name         = "test"
              source_instance_template = google_compute_instance_template.default.id
              metadata {
                foo = "bar"
                hey = "oh"
                block-project-ssh-keys = false
                }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_from_template']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_3(self):
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

    def test_unknown_1(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_from_template" "default" {
              name         = "test"
              source_instance_template = google_compute_instance_template.default.id
              metadata {
                foo = "bar"
                hey = "oh"
                }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_from_template']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_unknown_2(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_from_template" "default" {
              name         = "test"
              source_instance_template = google_compute_instance_template.default.id
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_from_template']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_success_1(self):
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

    def test_success_2(self):
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

    def test_success_3(self):
        hcl_res = hcl2.loads("""
            resource "google_compute_instance_from_template" "default" {
              name         = "test"
              source_instance_template = google_compute_instance_template.default.id
              metadata {
                foo = "bar"
                hey = "oh"
                block-project-ssh-keys = true
                }
            }
                """)
        resource_conf = hcl_res['resource'][0]['google_compute_instance_from_template']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
