import unittest
import hcl2

from checkov.terraform.checks.resource.aws.NeptuneClusterInstancePublic import check
from checkov.common.models.enums import CheckResult

class TestNeptuneClusterInstancePublic(unittest.TestCase):

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_neptune_cluster_instance" "example" {
  count              = 2
  cluster_identifier = aws_neptune_cluster.default.id
  engine             = "neptune"
  instance_class     = "db.r4.large"
  apply_immediately  = true
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_neptune_cluster_instance']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_explicit(self):
        hcl_res = hcl2.loads("""
resource "aws_neptune_cluster_instance" "example" {
  count               = 2
  cluster_identifier  = aws_neptune_cluster.default.id
  engine              = "neptune"
  instance_class      = "db.r4.large"
  apply_immediately   = true
  publicly_accessible = false
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_neptune_cluster_instance']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_neptune_cluster_instance" "example" {
  count               = 2
  cluster_identifier  = aws_neptune_cluster.default.id
  engine              = "neptune"
  instance_class      = "db.r4.large"
  apply_immediately   = true
  publicly_accessible = true
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_neptune_cluster_instance']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
