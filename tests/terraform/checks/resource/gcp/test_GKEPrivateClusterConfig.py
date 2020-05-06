import unittest

from checkov.terraform.checks.resource.gcp.GKEPrivateClusterConfig import check
from checkov.common.models.enums import CheckResult


class TestGKEPrivateClusterConfig(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster_bad'], 'monitoring_service': ['none'], 'enable_legacy_abac': [True], 'master_authorized_networks_config': [{'cidr_blocks': [{'cidr_block': ['0.0.0.0/0'], 'display_name': ['The world']}]}], 'master_auth': [{'username': ['test'], 'password': ['password']}], 'resource_labels': [{}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['google_cluster'], 'enable_legacy_abac': [False], 'resource_labels': [{'Owner': ['SomeoneNotWorkingHere']}], 'node_config': [{'image_type': ['cos']}], 'ip_allocation_policy': [{}], 'private_cluster_config': [{}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
