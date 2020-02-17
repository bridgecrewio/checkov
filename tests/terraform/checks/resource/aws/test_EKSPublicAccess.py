import unittest

from checkov.terraform.checks.resource.aws.EKSPublicAccess import check
from checkov.common.models.enums import CheckResult


class TestEKSPublicAccess(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['testcluster'], 'vpc_config': [{'endpoint_public_access': [True]}] }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


    def test_failure_empty(self):
        resource_conf = {'name': ['testcluster'], 'vpc_config': [{}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


    def test_success(self):
        resource_conf = {'name': ['testcluster'], 'vpc_config': [{'endpoint_public_access': [False]}] }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()


