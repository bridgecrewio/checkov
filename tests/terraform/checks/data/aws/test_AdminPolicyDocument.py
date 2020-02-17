import unittest

from checkov.terraform.checks.data.aws.AdminPolicyDocument import check
from checkov.common.models.enums import CheckResult


class TestAdminPolicyDocument(unittest.TestCase):

    def test_success(self):
        resource_conf = {
            "statement": [{
                "actions": ["Describe*"],
                "resources": ["arn:aws:s3:::my_corporate_bucket/*"]
            }]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {
            "statement": [{
                "actions": ["*"],
                "resources": ["*"]
            }]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)



if __name__ == '__main__':
    unittest.main()
