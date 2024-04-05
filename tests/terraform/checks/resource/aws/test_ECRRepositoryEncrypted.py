import unittest
import hcl2

from checkov.terraform.checks.resource.aws.ECRRepositoryEncrypted import check
from checkov.common.models.enums import CheckResult


class TestECRRepositoryEncrypted(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_ecr_repository" "foo" {
                  name                 = "bar"
                  image_tag_mutability = "MUTABLE"
                
                  image_scanning_configuration {
                    scan_on_push = true
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_ecr_repository']['foo']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_kms(self):
        hcl_res = hcl2.loads("""
                resource "aws_ecr_repository" "foo" {
                  name                 = "bar"
                  image_tag_mutability = "MUTABLE"

                  image_scanning_configuration {
                    scan_on_push = true
                  }
                  
                  encryption_configuration {
                    encryption_type = "KMS"
                  }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_ecr_repository']['foo']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

        def test_success_aes256(self):
            hcl_res = hcl2.loads("""
                    resource "aws_ecr_repository" "foo" {
                      name                 = "bar"
                      image_tag_mutability = "MUTABLE"

                      image_scanning_configuration {
                        scan_on_push = true
                      }
                      
                      encryption_configuration {
                        encryption_type = "AES256"
                      }
                    }
            """)
            resource_conf = hcl_res['resource'][0]['aws_ecr_repository']['foo']
            scan_result = check.scan_resource_conf(conf=resource_conf)
            self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
