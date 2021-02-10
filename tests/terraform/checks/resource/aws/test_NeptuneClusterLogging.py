import unittest
import hcl2

from checkov.terraform.checks.resource.aws.NeptuneClusterLogging import check
from checkov.common.models.enums import CheckResult

class TestNeptuneClusterLogging(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
            resource "aws_neptune_cluster" "test" {
              cluster_identifier                  = "neptune-cluster-demo"
              engine                              = "neptune"
              backup_retention_period             = 5
              preferred_backup_window             = "07:00-09:00"
              skip_final_snapshot                 = true
              iam_database_authentication_enabled = true
              apply_immediately                   = true
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_neptune_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "aws_neptune_cluster" "test" {
              cluster_identifier                  = "neptune-cluster-demo"
              engine                              = "neptune"
              backup_retention_period             = 5
              preferred_backup_window             = "07:00-09:00"
              skip_final_snapshot                 = true
              iam_database_authentication_enabled = true
              apply_immediately                   = true
              enable_cloudwatch_logs_exports      = ["audit"]
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_neptune_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
