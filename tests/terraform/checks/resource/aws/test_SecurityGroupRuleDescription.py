import unittest
import hcl2

from checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription import check
from checkov.common.models.enums import CheckResult


class TestSecurityGroupRuleDescription(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource aws_security_group_rule "ingress" {
  from_port = 443
  protocol = "TCP"
  security_group_id = aws_security_group.aurora_cluster_bastion_sg.id
  to_port = 443
  type = "ingress"
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource aws_security_group_rule "ingress" {
    description = "Allow HTTPS access"
    from_port = 443
    protocol = "TCP"
    security_group_id = aws_security_group.aurora_cluster_bastion_sg.id
    to_port = 443
    type = "ingress"
}
                """)
        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "sg_test" {
  description = "Security Group for Aurora Cluster Bastion Host"

  egress {
    description = "Allow egress communication"
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "-1"
    protocol    = "icmp"
    self        = "false"
    to_port     = "-1"
  }

  name = "bc-aurora-cluster-bastion-sg"

  tags = {
    Name = "bc-aurora-cluster-bastion-sg-BastionSecurityGroup"
  }

  vpc_id = var.vpc_id
}   
        """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['sg_test']
        result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_success2(self):
            hcl_res = hcl2.loads("""
    resource "aws_security_group" "sg_test" {
      description = "Security Group for Aurora Cluster Bastion Host"

      egress {
        description = "Allow egress communication"
        cidr_blocks = ["0.0.0.0/0"]
        from_port   = "0"
        protocol    = "-1"
        self        = "false"
        to_port     = "0"
      }

      ingress {
        description = "Allow ingress ICMP for SSH"
        cidr_blocks = ["0.0.0.0/0"]
        from_port   = "-1"
        protocol    = "icmp"
        self        = "false"
        to_port     = "-1"
      }

      name = "bc-aurora-cluster-bastion-sg"

      tags = {
        Name = "bc-aurora-cluster-bastion-sg-BastionSecurityGroup"
      }

      vpc_id = var.vpc_id
    }   
            """)
            resource_conf = hcl_res['resource'][0]['aws_security_group']['sg_test']
            result = check.scan_resource_conf(conf=resource_conf)
            self.assertEqual(result, CheckResult.PASSED)


if __name__ == '__main__':
    unittest.main()
