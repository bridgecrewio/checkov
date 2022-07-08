import unittest

from checkov.terraform.checks.resource.gcp.GKEClusterLogging import check
from checkov.common.models.enums import CheckResult


class TestGKEClusterLogging(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["my-gke-cluster"],
            "location": ["us-central1"],
            "remove_default_node_pool": [True],
            "initial_node_count": [1],
            "logging_service": ["none"],
            "master_auth": [
                {
                    "username": [""],
                    "password": [""],
                    "client_certificate_config": [{"issue_client_certificate": [False]}],
                }
            ],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["my-gke-cluster"],
            "location": ["us-central1"],
            "remove_default_node_pool": [True],
            "initial_node_count": [1],
            "master_auth": [
                {
                    "username": [""],
                    "password": [""],
                    "client_certificate_config": [{"issue_client_certificate": [False]}],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
