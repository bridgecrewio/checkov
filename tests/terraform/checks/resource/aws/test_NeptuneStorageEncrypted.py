import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.NeptuneClusterStorageEncrypted import check


class TestNeptuneClusterStorageEncrypted(unittest.TestCase):
    def test_failure(self):
        resource_conf = {"cluster_identifier": ["neptune-cluster-demo"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_settofalse(self):
        resource_conf = {
            "cluster_identifier": ["neptune-cluster-demo"],
            "storage_encrypted": [False],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "cluster_identifier": ["neptune-cluster-demo"],
            "storage_encrypted": [True],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
