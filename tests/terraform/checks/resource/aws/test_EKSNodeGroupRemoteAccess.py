import unittest
import hcl2

from checkov.terraform.checks.resource.aws.EKSNodeGroupRemoteAccess import check
from checkov.common.models.enums import CheckResult


class TestEKSNodeGroupRemoteAccess(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_eks_node_group" "test" {
  cluster_name    = aws_eks_cluster.example.name
  node_group_name = "example"
  node_role_arn   = aws_iam_role.example.arn
  subnet_ids      = aws_subnet.example[*].id

  remote_access {
    ec2_ssh_key = "some-key"
  }

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_eks_node_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_eks_node_group" "test" {
  cluster_name    = aws_eks_cluster.example.name
  node_group_name = "example"
  node_role_arn   = aws_iam_role.example.arn
  subnet_ids      = aws_subnet.example[*].id

  remote_access {
    ec2_ssh_key = "some-key"
    source_security_group_ids = "some-group"
  }

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_eks_node_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_implicit(self):
        hcl_res = hcl2.loads("""
resource "aws_eks_node_group" "test" {
  cluster_name    = aws_eks_cluster.example.name
  node_group_name = "example"
  node_role_arn   = aws_iam_role.example.arn
  subnet_ids      = aws_subnet.example[*].id

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_eks_node_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
