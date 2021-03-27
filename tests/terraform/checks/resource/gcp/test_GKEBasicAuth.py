import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GKEBasicAuth import check


class TestGKEBasicAuth(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["google_cluster_bad"],
            "monitoring_service": ["none"],
            "enable_legacy_abac": [True],
            "master_authorized_networks_config": [
                {
                    "cidr_blocks": [
                        {
                            "cidr_block": ["0.0.0.0/0"],
                            "display_name": ["The world"],
                        }
                    ]
                }
            ],
            "master_auth": [
                {
                    "username": ["test"],
                    "password": ["password"],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        resource_conf = {
            "name": ["google_cluster"],
            "monitoring_service": ["monitoring.googleapis.com"],
            "master_authorized_networks_config": [{}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["google_cluster"],
            "monitoring_service": ["monitoring.googleapis.com"],
            "master_authorized_networks_config": [{}],
            "master_auth": [
                {
                    "client_certificate_config": [
                        {
                            "issue_client_certificate": [False],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_basic_out_if_username_and_password_are_present_but_empty(self):
        resource_conf = {
            "name": ["google_cluster"],
            "monitoring_service": ["monitoring.googleapis.com"],
            "master_authorized_networks_config": [{}],
            "master_auth": [
                {
                    "username": [""],
                    "password": [""],
                    "client_certificate_config": [
                        {
                            "issue_client_certificate": [False],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
