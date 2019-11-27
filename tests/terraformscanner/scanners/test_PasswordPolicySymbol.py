import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.scanners.PasswordPolicySymbol import PasswordPolicySymbol


class TestPasswordPolicySymbol(unittest.TestCase):

    def test_success(self):
        scanner = PasswordPolicySymbol()
        resource_conf = {
            "minimum_password_length": 8,
            "require_lowercase_characters": True,
            "require_numbers": True,
            "require_uppercase_characters": True,
            "require_symbols": True,
            "allow_users_to_change_password": True,
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)

    def test_failure(self):
        scanner = PasswordPolicySymbol()
        resource_conf = {
            "minimum_password_length": 8,
            "require_lowercase_characters": False,
            "require_numbers": True,
            "require_uppercase_characters": True,
            "require_symbols": False,
            "allow_users_to_change_password": True,
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_failure_on_missing_property(self):
        scanner = PasswordPolicySymbol()
        resource_conf = {
            "minimum_password_length": 8,
            "require_lowercase_characters": True,
            "require_numbers": True,
            "allow_users_to_change_password": True,
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)


if __name__ == '__main__':
    unittest.main()
