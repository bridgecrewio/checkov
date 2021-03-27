import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.RDSPubliclyAccessible import check


class TestRedshitClusterPubliclyAccessible(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_redshift_cluster" "public" {
            cluster_identifier  = "tf-redshift-cluster"
            database_name       = "mydb"
            master_username     = "foo"
            master_password     = "Mustbe8characters"
            node_type           = "dc1.large"
            publicly_accessible = true
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_redshift_cluster"]["public"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
          resource "aws_redshift_cluster" "private" {
            cluster_identifier  = "tf-redshift-cluster"
            database_name       = "mydb"
            master_username     = "foo"
            master_password     = "Mustbe8characters"
            node_type           = "dc1.large"
            publicly_accessible = false
          }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_redshift_cluster"]["private"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
