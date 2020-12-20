import unittest

import hcl2

from checkov.terraform.checks.resource.aws.AuroraEncryption import check
from checkov.common.models.enums import CheckResult


class TestAuroraEncryption(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource "aws_rds_cluster" "test" {
            cluster_identifier      = "aurora-cluster-demo"
            engine                  = "aurora-mysql"
            engine_version          = "5.7.mysql_aurora.2.03.2"
            availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
            database_name           = "mydb"
            master_username         = "foo"
            master_password         = "bar"
            backup_retention_period = 5
            preferred_backup_window = "07:00-09:00"
            storage_encrypted       = true
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_serverless_default(self):
        hcl_res = hcl2.loads("""
        resource "aws_rds_cluster" "test" {
            cluster_identifier      = "aurora-cluster-demo"
            availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
            database_name           = "mydb"
            master_username         = "foo"
            master_password         = "bar"
            backup_retention_period = 5
            preferred_backup_window = "07:00-09:00"
            engine_mode             = "serverless"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    # If engine_mode is serverless then storage_encrypted should be ignored
    def test_success_serverless_enc_off(self):
        hcl_res = hcl2.loads("""
        resource "aws_rds_cluster" "test" {
            cluster_identifier      = "aurora-cluster-demo"
            availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
            database_name           = "mydb"
            master_username         = "foo"
            master_password         = "bar"
            backup_retention_period = 5
            preferred_backup_window = "07:00-09:00"
            engine_mode             = "serverless"
            storage_encrypted       = false
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_explicit(self):
        hcl_res = hcl2.loads("""
        resource "aws_rds_cluster" "test" {
            cluster_identifier      = "aurora-cluster-demo"
            engine                  = "aurora-mysql"
            engine_version          = "5.7.mysql_aurora.2.03.2"
            availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
            database_name           = "mydb"
            master_username         = "foo"
            master_password         = "bar"
            backup_retention_period = 5
            preferred_backup_window = "07:00-09:00"
            storage_encrypted       = false
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_default(self):
        hcl_res = hcl2.loads("""
        resource "aws_rds_cluster" "test" {
            cluster_identifier      = "aurora-cluster-demo"
            engine                  = "aurora-mysql"
            engine_version          = "5.7.mysql_aurora.2.03.2"
            availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
            database_name           = "mydb"
            master_username         = "foo"
            master_password         = "bar"
            backup_retention_period = 5
            preferred_backup_window = "07:00-09:00"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

if __name__ == '__main__':
    unittest.main()
