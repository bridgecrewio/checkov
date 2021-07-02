import unittest
import hcl2

from checkov.terraform.checks.provider.aws.defaulttags import check
from checkov.common.models.enums import CheckResult


class TestDefaultTags(unittest.TestCase):

    def test_failure_no_default_tags(self):
        hcl_res = hcl2.loads("""
          provider "aws" {
            region     = "${var.region}"
          }
        """)
        provider_conf = hcl_res['provider'][0]['aws']
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_empty_map(self):
        hcl_res = hcl2.loads("""
          provider "aws" {
            region     = "${var.region}"
            default_tags {
              tags = {
              }
            }
          }
        """)
        provider_conf = hcl_res['provider'][0]['aws']
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_default_tags(self):
        hcl_res = hcl2.loads("""
          provider "aws" {
            region     = "${var.region}"
            default_tags {
              tags = {
                Environment = "Test"
                Project     = "Test"
              }
            }
          }
        """)
        provider_conf = hcl_res['provider'][0]['aws']
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
