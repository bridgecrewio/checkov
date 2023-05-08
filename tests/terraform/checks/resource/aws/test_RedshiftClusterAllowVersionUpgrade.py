import unittest

import hcl2

from checkov.terraform.checks.resource.aws.RedshiftClusterAllowVersionUpgrade import check
from checkov.common.models.enums import CheckResult


class TestRedshiftClusterAllowVersionUpgrade(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
               resource "aws_redshift_cluster" "default" {
                  cluster_identifier = "tf-redshift-cluster"
                  database_name      = "mydb"
                  master_username    = "foo"
                  master_password    = "Mustbe8characters"  # checkov:skip=CKV_SECRET_6 test secret
                  node_type          = "dc1.large"
                  cluster_type       = "single-node"
                  allow_version_upgrade = false
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_missing_attribute(self):
        hcl_res = hcl2.loads("""
                   resource "aws_redshift_cluster" "default" {
                      cluster_identifier = "tf-redshift-cluster"
                      database_name      = "mydb"
                      master_username    = "foo"
                      master_password    = "Mustbe8characters"
                      node_type          = "dc1.large"
                      cluster_type       = "single-node"
                    }
                   """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
               resource "aws_redshift_cluster" "default" {
                  cluster_identifier = "tf-redshift-cluster"
                  database_name      = "mydb"
                  master_username    = "foo"
                  master_password    = "Mustbe8characters"
                  node_type          = "dc1.large"
                  cluster_type       = "single-node"
                  allow_version_upgrade = true
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
