import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.data.aws.StarActionPolicyDocument import check


class TestStarActionPolicyDocument(unittest.TestCase):
    def test_success(self):
        resource_conf = {
            "statement": [
                {
                    "actions": [["s3:*"]],
                    "resources": [["arn:aws:s3:::my_corporate_bucket/*"]],
                    "effect": ["Allow"],
                }
            ]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {
            "statement": [
                {
                    "actions": [["*"]],
                    "resources": [["arn:aws:s3:::my_corporate_bucket/*"]],
                    "effect": ["Allow"],
                }
            ]
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
