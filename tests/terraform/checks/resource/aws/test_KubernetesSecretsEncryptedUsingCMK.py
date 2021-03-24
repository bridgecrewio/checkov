import unittest

import hcl2

from checkov.terraform.checks.resource.aws.KubernetesSecretsEncryptedUsingCMK import check
from checkov.common.models.enums import CheckResult


class TestKubernetesSecretsEncryptedUsingCMK(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
            resource "aws_eks_cluster" "test" {
              name     = "example"
              role_arn = aws_iam_role.example.arn
            
              vpc_config {
                    subnet_ids = [aws_subnet.example1.id, aws_subnet.example2.id]
                }
              }
        """)
        resource_conf = hcl_res['resource'][0]['aws_eks_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
            resource "aws_eks_cluster" "test" {
              name     = "example"
              role_arn = aws_iam_role.example.arn

              vpc_config {
                    subnet_ids = [aws_subnet.example1.id, aws_subnet.example2.id]
                }
             encryption_config {
                            resources = ["test"]
                            provider {
                                key_arn = "test"
                             }
                      }   
              }
        """)
        resource_conf = hcl_res['resource'][0]['aws_eks_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_eks_cluster" "test" {
                      name     = "example"
                      role_arn = aws_iam_role.example.arn

                      vpc_config {
                        subnet_ids = [aws_subnet.example1.id, aws_subnet.example2.id]
                      }
                      
                      encryption_config {
                            resources = ["secrets"]
                            provider {
                                key_arn = "test"
                             }
                      }
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_eks_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
