import unittest

import hcl2

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.cloudwatchLogGroupRetention import check


class TestCloudwatchLogGroupRetention(unittest.TestCase):
    def test_failure(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_cloudwatch_log_group" "test-lg" {
            name   = "test-lg"
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_cloudwatch_log_group"]["test-lg"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads(
            """
            resource "aws_cloudwatch_log_group" "test-lg" {
            name   = "test-lg"
            retention_in_days = 3
            }
        """
        )
        resource_conf = hcl_res["resource"][0]["aws_cloudwatch_log_group"]["test-lg"]
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
