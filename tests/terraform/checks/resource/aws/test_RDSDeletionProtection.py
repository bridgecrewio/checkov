import unittest

import hcl2

from checkov.terraform.checks.resource.aws.RDSDeletionProtection import check
from checkov.common.models.enums import CheckResult


class TestRDSDeletionProtection(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_rds_cluster" "default" {
                    cluster_identifier      = "aurora-cluster-demo"
                    availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
                    database_name           = "mydb"
                    master_username         = "foo"
                    master_password         = "bar"
                    backup_retention_period = 5
                    preferred_backup_window = "07:00-09:00"
                    deletion_protection = false
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_missing_attribute(self):
        hcl_res = hcl2.loads("""
                resource "aws_rds_cluster" "default" {
                    cluster_identifier      = "aurora-cluster-demo"
                    availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
                    database_name           = "mydb"
                    master_username         = "foo"
                    master_password         = "bar"
                    backup_retention_period = 5
                    preferred_backup_window = "07:00-09:00"
                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_rds_cluster" "default" {
                    cluster_identifier      = "aurora-cluster-demo"
                    availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
                    database_name           = "mydb"
                    master_username         = "foo"
                    master_password         = "bar"
                    backup_retention_period = 5
                    preferred_backup_window = "07:00-09:00"
                    deletion_protection = true

                }
                """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['default']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
