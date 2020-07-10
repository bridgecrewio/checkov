import unittest

from checkov.terraform.checks.resource.gcp.GKEPodSecurityPolicyEnabled import check
from checkov.common.models.enums import CheckResult


class TestGKEPodSecurityPolicyEnabled(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster'], 'enable_legacy_abac': [False], 'resource_labels': [{'Owner': ['SomeoneNotWorkingHere']}], 'node_config': [{'image_type': ['cos']}], 'ip_allocation_policy': [{}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['google_cluster'], 'monitoring_service': ['monitoring.googleapis.com'], 'master_authorized_networks_config': [{}], 'master_auth': [{'client_certificate_config': [{'issue_client_certificate': [False]}]}], 'node_config': [{'image_type': ['not-cos']}], 'pod_security_policy_config': [{'enabled': [True]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
