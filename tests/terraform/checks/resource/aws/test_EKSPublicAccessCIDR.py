import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.EKSPublicAccessCIDR import check


class TestEKSPublicAccessCIDR(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["testcluster"],
            "vpc_config": [{"public_access_cidrs": [{"0.0.0.0/0"}]}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_empty(self):
        resource_conf = {"name": ["testcluster"], "vpc_config": [{}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_empty_cidr(self):
        resource_conf = {
            "name": ["testcluster"],
            "vpc_config": [{"public_access_cidrs": [{}]}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["testcluster"],
            "vpc_config": [{"public_access_cidrs": [{"10.0.0.0/16"}]}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_endpoint(self):
        resource_conf = {
            "name": ["testcluster"],
            "vpc_config": [{"endpoint_public_access": [False]}],
        }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
