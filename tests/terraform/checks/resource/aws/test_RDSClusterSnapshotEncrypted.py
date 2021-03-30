import unittest
import hcl2

from checkov.terraform.checks.resource.aws.RDSClusterSnapshotEncrypted import check
from checkov.common.models.enums import CheckResult


class TestRDSClusterSnapshotEncrypted(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_db_cluster_snapshot" "example" {
              db_cluster_identifier          = aws_rds_cluster.example.id
              db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_db_cluster_snapshot']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "aws_db_cluster_snapshot" "example" {
              db_cluster_identifier          = aws_rds_cluster.example.id
              db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
              storage_encrypted = false
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_db_cluster_snapshot']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
            resource "aws_db_cluster_snapshot" "example" {
              db_cluster_identifier          = aws_rds_cluster.example.id
              db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
              storage_encrypted = true
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_db_cluster_snapshot']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
