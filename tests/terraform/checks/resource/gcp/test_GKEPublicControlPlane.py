import unittest

from checkov.terraform.checks.resource.gcp.GKEPublicControlPlane import check
from checkov.common.models.enums import CheckResult


class TestGKEPublicControlPlane(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster_bad'], 'monitoring_service': ['none'], 'enable_legacy_abac': [True], 'master_authorized_networks_config': [{'cidr_blocks': [{'cidr_block': ['0.0.0.0/0'], 'display_name': ['The world']}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['google_cluster'], 'enable_legacy_abac': [False]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
