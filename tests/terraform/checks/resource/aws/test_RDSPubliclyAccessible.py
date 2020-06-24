import unittest
import hcl2

from checkov.terraform.checks.resource.aws.RDSPubliclyAccessible import check
from checkov.common.models.enums import CheckResult


class TestRDSPubliclyAccessible(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource aws_rds_cluster_instance "rds_cluster_public" {
  cluster_identifier = "id"
  instance_class = "foo-bar"
  publicly_accessible = true
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster_instance']['rds_cluster_public']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
        resource aws_rds_cluster_instance "rds_cluster_public" {
          cluster_identifier = "id"
          instance_class = "foo-bar"
          publicly_accessible = false
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster_instance']['rds_cluster_public']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
        hcl_res = hcl2.loads("""
           resource aws_rds_cluster_instance "rds_cluster_public" {
             cluster_identifier = "id"
             instance_class = "foo-bar"
           }
           """)
        resource_conf = hcl_res['resource'][0]['aws_rds_cluster_instance']['rds_cluster_public']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
