import unittest

from checkov.terraform.checks.resource.aws.PasswordPolicyUppercaseLetter import check
from checkov.common.models.enums import CheckResult


class TestPasswordPolicyUpperCaseLetter(unittest.TestCase):

    def test_success(self):
        resource_conf = {
            "minimum_password_length": [15],
            "require_lowercase_characters": [True],
            "require_numbers": [True],
            "require_uppercase_characters": [True],
            "require_symbols": [True],
            "allow_users_to_change_password": [True],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {
            "minimum_password_length": [15],
            "require_lowercase_characters": [True],
            "require_numbers": [True],
            "require_uppercase_characters": [False],
            "require_symbols": [True],
            "allow_users_to_change_password": [True],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_on_missing_property(self):
        resource_conf = {
            "minimum_password_length": [15],
            "require_lowercase_characters": [True],
            "require_numbers": [True],
            "require_symbols": [True],
            "allow_users_to_change_password": [True],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
