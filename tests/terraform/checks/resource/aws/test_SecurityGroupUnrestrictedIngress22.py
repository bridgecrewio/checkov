import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress22 import check


class TestSecurityGroupUnrestrictedIngress22(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}  
        """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['bar-sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['bar-sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
