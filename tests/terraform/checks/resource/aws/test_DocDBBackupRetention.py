import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.DocDBBackupRetention import check


class TestDocDBBackupRetention(unittest.TestCase):

    def test_failure(self):
        # No value provided (default is 1)
        resource_conf = {"cluster_identifier": "my-docdb-cluster"}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

        # Provided value is not adequate
        resource_conf = {"cluster_identifier": "my-docdb-cluster",
                         "backup_retention_period": 2}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"cluster_identifier": "my-docdb-cluster",
                         "backup_retention_period": 8}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
