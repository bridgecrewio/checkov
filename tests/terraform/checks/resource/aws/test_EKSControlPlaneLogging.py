import unittest

from checkov.terraform.checks.resource.aws.EKSControlPlaneLogging import check
from checkov.common.models.enums import CheckResult


class TestEKSControlPlaneLogging(unittest.TestCase):
    def test_failure(self):
        resource_conf = {'name': ['testcluster'], 'enabled_cluster_log_types': [['api', 'audit']]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_empty(self):
        resource_conf = {'name': ['testcluster']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['testcluster'], 'enabled_cluster_log_types': [['api', 'audit', 'authenticator', 'controllerManager', 'scheduler']]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['testcluster'], 'enabled_cluster_log_types': []}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
