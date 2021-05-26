import unittest

import hcl2

from checkov.terraform.checks.data.aws.AdminPolicyDocument import check
from checkov.common.models.enums import CheckResult


class TestAdminPolicyDocument(unittest.TestCase):

    def test_success(self):
        resource_conf = {'version': ['2012-10-17'], 'statement': [{'actions': [['s3:Describe*']], 'resources': [['*']], 'effect': ['Allow']}]}
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {'version': ['2012-10-17'], 'statement': [{'actions': [['*']], 'resources': [['*']], 'effect': ['Allow']}]}
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_no_effect(self):
        resource_conf = {'version': ['2012-10-17'], 'statement': [{'actions': [['*']], 'resources': [['*']]}]}
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_passed_list_statement(self):
        hcl_res = hcl2.loads("""
            data "aws_iam_policy_document" "default" {
              statement = [{
                actions = ["s3:GetObject"]
            
                resources = ["${aws_s3_bucket.default.arn}/*"]
            
                principals {
                  type        = "AWS"
                  identifiers = ["*"]
                }
              }]
            
              # Support replication ARNs
              statement = ["${flatten(data.aws_iam_policy_document.replication.*.statement)}"]
            
              # Support deployment ARNs
              statement = ["${flatten(data.aws_iam_policy_document.deployment.*.statement)}"]
            }
        """)
        resource_conf = hcl_res['data'][0]['aws_iam_policy_document']['default']
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
