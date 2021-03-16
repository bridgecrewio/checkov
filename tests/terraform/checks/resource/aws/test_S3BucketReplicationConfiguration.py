import unittest
import hcl2

from checkov.terraform.checks.resource.aws.S3BucketReplicationConfiguration import check
from checkov.common.models.enums import CheckResult


class TestS3BucketReplicationConfiguration(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_s3_bucket" "test" {
                      bucket = "my-tf-test-bucket"
                      acl    = "private"
                    
                      tags = {
                        Name        = "My bucket"
                        Environment = "Dev"
                      }
                      replication_configuration {                    
                        rules {
                          id     = "foobar"
                          prefix = "foo"
                          status = "Enabled"
                    
                          destination {
                            bucket        = aws_s3_bucket.destination.arn
                            storage_class = "STANDARD"
                          }
                        }
                      }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_param(self):
        hcl_res = hcl2.loads("""
                resource "aws_s3_bucket" "test" {
                      bucket = "my-tf-test-bucket"
                      acl    = "private"

                      tags = {
                        Name        = "My bucket"
                        Environment = "Dev"
                      }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_s3_bucket" "test" {
                      bucket = "my-tf-test-bucket"
                      acl    = "private"
                    
                      tags = {
                        Name        = "My bucket"
                        Environment = "Dev"
                      }
                      replication_configuration { 
                        role = aws_iam_role.replication.arn
                        rules {
                          id     = "foobar"
                          prefix = "foo"
                          status = "Enabled"
                    
                          destination {
                            bucket        = aws_s3_bucket.destination.arn
                            storage_class = "STANDARD"
                          }
                        }
                      }
                }
        """)
        resource_conf = hcl_res['resource'][0]['aws_s3_bucket']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
