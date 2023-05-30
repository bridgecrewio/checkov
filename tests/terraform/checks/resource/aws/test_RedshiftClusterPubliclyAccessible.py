import unittest
import hcl2

from checkov.terraform.checks.resource.aws.RedshitClusterPubliclyAvailable import check
from checkov.common.models.enums import CheckResult


class TestRedshitClusterPubliclyAccessible(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
          resource "aws_redshift_cluster" "public" {
            cluster_identifier  = "tf-redshift-cluster"
            database_name       = "mydb"
            master_username     = "foo"
            master_password     = "Mustbe8characters"  # checkov:skip=CKV_SECRET_6 test secret
            node_type           = "dc1.large"
            publicly_accessible = true
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['public']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
          resource "aws_redshift_cluster" "public" {
            cluster_identifier  = "tf-redshift-cluster"
            database_name       = "mydb"
            master_username     = "foo"
            master_password     = "Mustbe8characters"
            node_type           = "dc1.large"
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['public']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
          resource "aws_redshift_cluster" "private" {
            cluster_identifier  = "tf-redshift-cluster"
            database_name       = "mydb"
            master_username     = "foo"
            master_password     = "Mustbe8characters"
            node_type           = "dc1.large"
            publicly_accessible = false
          }
        """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['private']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
