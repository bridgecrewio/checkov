import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DocDBEncryption import check


class TestDocDBEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {"cluster_identifier": "my-docdb-cluster",
                         "storage_encrypted": False}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"cluster_identifier": "my-docdb-cluster",
                         "storage_encrypted": True}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
