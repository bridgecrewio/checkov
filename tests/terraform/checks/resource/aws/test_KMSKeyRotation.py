import unittest
import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.KMSKeyRotation import check


class TestKMSKeyRotation(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                    resource "aws_kms_key" "example" {                    
                      name = "example"
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_kms_key']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                    resource "aws_kms_key" "example" {                    
                      name                = "example"
                      enable_key_rotation = true
                    }
                """)
        resource_conf = hcl_res['resource'][0]['aws_kms_key']['example']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
