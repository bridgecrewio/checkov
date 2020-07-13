import unittest

from checkov.terraform.checks.resource.aws.RedshiftClusterEncryption import check
from checkov.common.models.enums import CheckResult


class TestRedshiftClusterEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "cluster_identifier": ["tf-redshift-cluster"],
            "database_name": ["mydb"],
            "master_username": ["foo"],
            "master_password": ["Mustbe8characters"],
            "node_type": ["dc1.large"],
            "cluster_type": ["single-node"]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "cluster_identifier": ["tf-redshift-cluster"],
            "database_name": ["mydb"],
            "master_username": ["foo"],
            "master_password": ["Mustbe8characters"],
            "node_type": ["dc1.large"],
            "cluster_type": ["single-node"],
            "encrypted": [True]
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
