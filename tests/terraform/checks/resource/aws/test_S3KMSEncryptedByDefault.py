import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3KMSEncryptedByDefault import check


class TestS3KMSEncryptedByDefault(unittest.TestCase):

    def test_failure1(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket" "mybucket" {
          bucket = "mybucket"
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['mybucket']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        hcl_res = hcl2.loads("""
        resource "aws_s3_bucket" "mybucket" {
          bucket = "mybucket"
        
          server_side_encryption_configuration {
            rule {
              apply_server_side_encryption_by_default {
                sse_algorithm     = "AES256"
              }
            }
          }
        }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['mybucket']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
            resource "aws_s3_bucket" "mybucket" {
              bucket = "mybucket"
            
              server_side_encryption_configuration {
                rule {
                  apply_server_side_encryption_by_default {
                    kms_master_key_id = aws_kms_key.mykey.arn
                    sse_algorithm     = "aws:kms"
                  }
                }
              }
            }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['mybucket']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
