import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.GlueDataCatalogEncryption import check
import hcl2

class TestGlueDataCatalogEncryption(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
resource "aws_glue_data_catalog_encryption_settings" "test" {
  data_catalog_encryption_settings {
    connection_password_encryption {
      return_connection_password_encrypted = false
    }
    encryption_at_rest {
      catalog_encryption_mode = "DISABLED"
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_glue_data_catalog_encryption_settings']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
resource "aws_glue_data_catalog_encryption_settings" "test" {
  data_catalog_encryption_settings {
    connection_password_encryption {
      aws_kms_key_id                       = aws_kms_key.test.arn
      return_connection_password_encrypted = true
    }
    encryption_at_rest {
      catalog_encryption_mode = "SSE-KMS"
      sse_aws_kms_key_id      = aws_kms_key.test.arn
    }
  }
}
        """)
        resource_conf = hcl_res['resource'][0]['aws_glue_data_catalog_encryption_settings']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
