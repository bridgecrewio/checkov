import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.SecurityGroupUnrestrictedIngress80 import check


class TestSecurityGroupUnrestrictedIngress80(unittest.TestCase):

    def test_failure_ipv4(self):
        hcl_res = hcl2.loads("""
        resource "aws_security_group" "bar-sg" {
          name   = "sg-bar"
          vpc_id = aws_vpc.main.id
        
          ingress {
            from_port = 80
            to_port   = 80
            protocol  = "tcp"
            cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
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

    def test_failure_0_0(self):
        hcl_res = hcl2.loads("""
        resource "aws_security_group" "bar-sg" {
          name   = "sg-bar"
          vpc_id = aws_vpc.main.id

          ingress {
            from_port = 0
            to_port   = 0
            protocol  = "tcp"
            cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
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

    def test_failure_ipv6(self):
        hcl_res = hcl2.loads("""
        resource "aws_security_group" "bar-sg" {
          name   = "sg-bar"
          vpc_id = aws_vpc.main.id

          ingress {
            from_port = 80
            to_port   = 80
            protocol  = "tcp"
            ipv6_cidr_blocks = ["192.168.0.0/16", "::/0"]
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

    def test_success_different_port(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 222
    to_port   = 222
    protocol  = "tcp"
    cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
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

    def test_success_no_cidr(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
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

    def test_success_null_cidr(self):
        hcl_res = hcl2.loads("""
    resource "aws_security_group" "bar-sg" {
      name   = "sg-bar"
      vpc_id = aws_vpc.main.id

      ingress = [{
        from_port = 80
        to_port   = 80
        protocol  = "tcp"
        security_groups = [aws_security_group.foo-sg.id]
        description = "foo"
        cidr_blocks = null
      }]

      egress = [{
        from_port = 0
        to_port   = 0
        protocol  = "-1"
        cidr_blocks = null
      }]
    }
            """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['bar-sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_null_ipv6(self):
        hcl_res = hcl2.loads("""
    resource "aws_security_group" "bar-sg" {
      name   = "sg-bar"
      vpc_id = aws_vpc.main.id

      ingress = [{
        ipv6_cidr_blocks = null
        from_port = 80
        to_port   = 80
        protocol  = "tcp"
        security_groups = [aws_security_group.foo-sg.id]
        description = "foo"
        cidr_blocks = null
      }]

      egress = [{
        from_port = 0
        to_port   = 0
        protocol  = "-1"
        cidr_blocks = null
      }]
    }
            """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['bar-sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_cidr(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = ["192.168.0.0/16"]
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

    def test_failure_combined_ingress(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    cidr_blocks = ["192.168.0.0/16", "0.0.0.0/0"]
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

    def test_success_combined_ingress(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    security_groups = [aws_security_group.foo-sg.id]
    cidr_blocks = ["192.168.0.0/16"]
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

    def test_success_egress_only(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

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

    def test_ingress_rules_list(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "inline_rules" {
  description = "SG with inline rules"
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "Wide Open"
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      security_groups  = []
      protocol         = "-1"
      self             = false
      to_port          = 65535
    }
  ]
}
""")
        conf = hcl_res['resource'][0]['aws_security_group']['inline_rules']
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_failure_separate_rule_cidr(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group_rule" "ingress" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["192.168.0.0/16", "0.0.0.0/0"]
  security_group_id = aws_security_group.bar-sg.id
}
        """)

        resource_conf = hcl_res['resource'][0]['aws_security_group']['bar-sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

        resource_conf = hcl_res['resource'][1]['aws_security_group_rule']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_pass_separate_rule_cidr(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group_rule" "ingress" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["192.168.0.0/16"]
  security_group_id = aws_security_group.bar-sg.id
}
        """)

        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_unknown_separate_rule_egress(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group_rule" "egress" {
  type              = "egress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bar-sg.id
}
        """)

        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['egress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.UNKNOWN, scan_result)

    def test_pass_separate_rule_source_sg(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group_rule" "ingress" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  source_security_group_id       = "sg-123456"
  security_group_id = aws_security_group.bar-sg.id
}
        """)

        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_pass_separate_rule_different_port(self):
        hcl_res = hcl2.loads("""
resource "aws_security_group_rule" "ingress" {
  type              = "ingress"
  from_port         = 222
  to_port           = 222
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bar-sg.id
}
        """)

        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['ingress']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
