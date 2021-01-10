import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.GlueSecurityConfiguration import check
import hcl2

class TestGlueSecurityConfiguration(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_glue_security_configuration" "test" {
  name = "example"

  encryption_configuration {
    cloudwatch_encryption {
      cloudwatch_encryption_mode = "DISABLED"
    }

    job_bookmarks_encryption {
      job_bookmarks_encryption_mode = "DISABLED"
    }

    s3_encryption {
      kms_key_arn        = data.aws_kms_key.example.arn
      s3_encryption_mode = "SSE-KMS"
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_glue_security_configuration']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_glue_security_configuration" "test" {
  name = "example"

  encryption_configuration {
    cloudwatch_encryption {
      cloudwatch_encryption_mode = "SSE-KMS"
      kms_key_arn        = aws_kms_key.example.arn
    }

    job_bookmarks_encryption {
      job_bookmarks_encryption_mode = "CSE-KMS"
      kms_key_arn        = aws_kms_key.example.arn
    }

    s3_encryption {
      kms_key_arn        = aws_kms_key.example.arn
      s3_encryption_mode = "SSE-KMS"
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_glue_security_configuration']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
