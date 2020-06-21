import unittest

import hcl2

from checkov.terraform.checks.resource.gcp.GKEUseCosImage import check
from checkov.common.models.enums import CheckResult


class TestGKEUseCosImage(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster_bad'], 'monitoring_service': ['none'], 'enable_legacy_abac': [True], 'master_authorized_networks_config': [{'cidr_blocks': [{'cidr_block': ['0.0.0.0/0'], 'display_name': ['The world']}]}], 'master_auth': [{'username': ['test'], 'password': ['password']}], 'resource_labels': [{}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['google_cluster'], 'enable_legacy_abac': [False], 'resource_labels': [{'Owner': ['SomeoneNotWorkingHere']}], 'node_config': [{'image_type': ['cos']}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_case_insensitive(self):
        resource_conf = {'name': ['google_cluster'], 'enable_legacy_abac': [False], 'resource_labels': [{'Owner': ['SomeoneNotWorkingHere']}], 'node_config': [{'image_type': ['COS_CONTAINERD']}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_remove_node_pool(self):
        hcl_res = hcl2.loads("""
                    resource "google_container_cluster" "primary" {
                      name     = "my-gke-cluster"
                      location = "us-central1"
                    
                      # We can't create a cluster with no node pool defined, but we want to only use
                      # separately managed node pools. So we create the smallest possible default
                      # node pool and immediately delete it.
                      
                      initial_node_count       = 1
                    
                      master_auth {
                        username = ""
                        password = ""
                    
                        client_certificate_config {
                          issue_client_certificate = false
                        }
                      }
                    }

                """)
        resource_conf = hcl_res['resource'][0]['google_container_cluster']['primary']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
