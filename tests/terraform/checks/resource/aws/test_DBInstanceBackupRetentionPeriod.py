import unittest
import hcl2

from checkov.terraform.checks.resource.aws.DBInstanceBackupRetentionPeriod import check
from checkov.common.models.enums import CheckResult


class TestDBInstanceBackupRetentionPeriod(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                            resource "aws_rds_cluster" "test" {
                              allocated_storage     = 10
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_bad_value_min(self):
        hcl_res = hcl2.loads("""
                            resource "aws_rds_cluster" "test" {
                              allocated_storage       = 10
                              backup_retention_period = 0
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_bad_value_max(self):
        hcl_res = hcl2.loads("""
                            resource "aws_rds_cluster" "test" {
                              allocated_storage       = 10
                              backup_retention_period = 36
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                            resource "aws_rds_cluster" "test" {
                              allocated_storage       = 10
                              backup_retention_period = 35
                            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
