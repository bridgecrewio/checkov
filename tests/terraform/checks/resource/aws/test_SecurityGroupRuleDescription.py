import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.SecurityGroupRuleDescription import check


class TestSecurityGroupRuleDescription(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                            resource "aws_security_group" "example_sg" {
                              egress {
                                description = "Allow outgoing communication"
                                cidr_blocks = ["0.0.0.0/0"]
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "false"
                                to_port     = "0"
                              }
                              egress {
                                cidr_blocks = ["10.0.0.0/0"]
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "false"
                                to_port     = "0"
                              }
                              ingress {
                                description = "Self Reference"
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "true"
                                to_port     = "0"
                              }
                            
                              name = "example-lambda"
                            
                              tags = {
                                Name = "example-sg"
                              }
                            
                              vpc_id = aws_vpc.vpc.id
                            }
                """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['example_sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


    def test_sucess_sg_desc(self):
        hcl_res = hcl2.loads("""
                            resource "aws_security_group" "example_sg" {
                            description = "sg_desc"
                              egress {
                                description = "Allow outgoing communication"
                                cidr_blocks = ["0.0.0.0/0"]
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "false"
                                to_port     = "0"
                              }
                              egress {
                                description = "Egress description"
                                cidr_blocks = ["10.0.0.0/0"]
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "false"
                                to_port     = "0"
                              }
                            
                              ingress {
                                description = "Self Reference"
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "true"
                                to_port     = "0"
                              }
                            
                              name = "example-lambda"
                            
                              tags = {
                                Name = "example-sg"
                              }
                            
                              vpc_id = aws_vpc.vpc.id
                            }
                """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['example_sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_sg(self):
        hcl_res = hcl2.loads("""
                            resource "aws_security_group" "example_sg" {
                              description = "SG description"
                              egress {
                                description = "Allow outgoing communication"
                                cidr_blocks = ["0.0.0.0/0"]
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "false"
                                to_port     = "0"
                              }
                            
                              ingress {
                                description = "Self Reference"
                                from_port   = "0"
                                protocol    = "-1"
                                self        = "true"
                                to_port     = "0"
                              }
                            
                              name = "example-lambda"
                            
                              tags = {
                                Name = "example-sg"
                              }
                            
                              vpc_id = aws_vpc.vpc.id
                            }
                """)
        resource_conf = hcl_res['resource'][0]['aws_security_group']['example_sg']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_sg_rule(self):
        hcl_res = hcl2.loads("""
        resource "aws_security_group_rule" "example_sg_rule_failure" {
          type = "ingress"
          from_port = 3389
          to_port = 3389
          protocol = "tcp"
          cidr_blocks = "0.0.0.0/0"
          security_group_id = "sg-123456"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['example_sg_rule_failure']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_sg_rule(self):
        hcl_res = hcl2.loads("""
        resource "aws_security_group_rule" "example_sg_rule_success" {
          type = "ingress"
          description = "SG rule description"
          from_port = 3389
          to_port = 3389
          protocol = "tcp"
          cidr_blocks = "0.0.0.0/0"
          security_group_id = "sg-123456"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_security_group_rule']['example_sg_rule_success']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
