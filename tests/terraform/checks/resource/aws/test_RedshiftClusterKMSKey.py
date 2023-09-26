import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.RedshiftClusterKMSKey import check
import hcl2


class TestRedshiftClusterKMSKey(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_redshift_cluster" "test" {
                  cluster_identifier = "tf-redshift-cluster"
                  database_name      = "mydb"
                  master_username    = "foo"
                  master_password    = "Mustbe8characters"  # checkov:skip=CKV_SECRET_6 test secret
                  node_type          = "dc1.large"
                  cluster_type       = "single-node"
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_redshift_cluster" "test" {
                  cluster_identifier = "tf-redshift-cluster"
                  database_name      = "mydb"
                  master_username    = "foo"
                  master_password    = "Mustbe8characters"
                  node_type          = "dc1.large"
                  cluster_type       = "single-node"
                  kms_key_id         = "someKey"
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
