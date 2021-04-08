import unittest
import hcl2

from checkov.terraform.checks.resource.aws.RDSClusterEncrypted import check
from checkov.common.models.enums import CheckResult


class TestRDSClusterEncrypted(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_rds_global_cluster" "example" {
              provider = aws.primary
            
              global_cluster_identifier = "example"
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_global_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_explicit(self):
        hcl_res = hcl2.loads("""
            resource "aws_rds_global_cluster" "example" {
              provider = aws.primary
            
              global_cluster_identifier = "example"
              storage_encrypted         = false
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_global_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "aws_rds_global_cluster" "example" {
              provider = aws.primary
            
              global_cluster_identifier = "example"
              storage_encrypted         = true
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_global_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_with_source_db_cluster_identifier(self):
        hcl_res = hcl2.loads("""
            resource "aws_rds_global_cluster" "example" {
              provider = aws.primary
            
              global_cluster_identifier = "example"
              source_db_cluster_identifier = "some_arn"
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_global_cluster']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)


if __name__ == '__main__':
    unittest.main()
