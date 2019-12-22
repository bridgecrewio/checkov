import unittest

from checkov.terraform.checks.resource.gcp.GoogleContainerClusterNetworkPolicyEnabled import check
from checkov.terraform.models.enums import CheckResult


class GoogleContainerClusterNetworkPolicyEnabled(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['google_cluster'], 'network_policy': [{'enabled': False}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['google_cluster'], 'network_policy': [{'enabled': True}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
