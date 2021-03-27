import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3Encryption import check


class TestS3Encryption(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
            "logging": [{"target_bucket": "logging-bucket", "target_prefix": "log/"}],
            "server_side_encryption_configuration": [
                {
                    "rule": [
                        {
                            "apply_server_side_encryption_by_default": [
                                {"kms_master_key_id": "foo", "sse_algorithm": "aws:kms"}
                            ]
                        }
                    ]
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_oneline(self):
        hcl_res = hcl2.loads(
            """
        resource "aws_s3_bucket" "my" {
          bucket = "my-${lower(var.environment)}-my-${lower(var.my)}"
          acl    = "private"
          # Delete S3 Bucket even it has some objects in it
          force_destroy = "true"
          server_side_encryption_configuration {
            rule {
              apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
            }
          }
          versioning {
            enabled = false
          }
        }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["my"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_dynamic_value(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_s3_bucket" "default" {
              count         = local.enabled ? 1 : 0
              bucket        = module.this.id
              acl           = "private"
              force_destroy = var.force_destroy
              tags          = module.this.tags

              versioning {
                enabled = var.versioning_enabled
              }

              dynamic "logging" {
                for_each = var.access_log_bucket_name != "" ? [1] : []
                content {
                  target_bucket = var.access_log_bucket_name
                  target_prefix = "logs/${module.this.id}/"
                }
              }

              dynamic "server_side_encryption_configuration" {
                for_each = var.s3_bucket_encryption_enabled ? [1] : []

                content {
                  rule {
                    apply_server_side_encryption_by_default {
                      sse_algorithm = "AES256"
                    }
                  }
                }
              }

            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_s3_bucket"]["default"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
