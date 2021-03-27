import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.data.aws.AdminPolicyDocument import check


class TestAdminPolicyDocument(unittest.TestCase):
    def test_success(self):
        resource_conf = {
            "version": ["2012-10-17"],
            "statement": [
                {
                    "actions": [["s3:Describe*"]],
                    "resources": [["*"]],
                    "effect": ["Allow"],
                }
            ],
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {
            "version": ["2012-10-17"],
            "statement": [
                {"actions": [["*"]], "resources": [["*"]], "effect": ["Allow"]}
            ],
        }
        scan_result = check.scan_data_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == "__main__":
    unittest.main()
