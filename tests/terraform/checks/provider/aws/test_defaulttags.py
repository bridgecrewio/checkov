import unittest

import hcl2

from checkov.terraform.checks.provider.aws.defaulttags import check
from checkov.common.models.enums import CheckResult


class TestCredentials(unittest.TestCase):
    def test_failure_empty(self):
        hcl_res = hcl2.loads(
            """
            provider "aws" {}
            """
        )
        provider_conf = hcl_res["provider"][0]["aws"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            provider "aws" {
                region = "us-west-2"
                default_tags = {
                    tags = {
                        pike="permissions"
                    }
                }
            }
            """
        )
        provider_conf = hcl_res["provider"][0]["aws"]
        scan_result = check.scan_provider_conf(conf=provider_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
