import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.CloudwatchLogGroupKMSKey import check
import hcl2


class TestCloudwatchLogGroupKMSKey(unittest.TestCase):

    def test_failure(self):
        hcl_res = hcl2.loads("""
                resource "aws_cloudwatch_log_group" "test" {
                  retention_in_days = 1
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_redshift_cluster']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        hcl_res = hcl2.loads("""
                resource "aws_cloudwatch_log_group" "test" {
                  retention_in_days = 1
                  kms_key_id         = "someKey"
                }
            """)
        resource_conf = hcl_res['resource'][0]['aws_cloudwatch_log_group']['test']
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
