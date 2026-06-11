import unittest
from pathlib import Path

from checkov.terraform.checks.resource.aws.IAMRoleMaxSessionDuration import scanner
from checkov.common.models.enums import CheckResult


class TestIAMRoleMaxSessionDuration(unittest.TestCase):

    def test_success_no_max_session_duration(self):
        """Role with no max_session_duration set — defaults to 3600, should pass."""
        resource_conf = {
            "name": ["test_role"],
            "assume_role_policy": ['{"Version":"2012-10-17"}'],
        }
        result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.PASSED)

    def test_success_max_session_duration_3600(self):
        """Role with max_session_duration exactly 3600 — should pass."""
        resource_conf = {
            "name": ["test_role"],
            "assume_role_policy": ['{"Version":"2012-10-17"}'],
            "max_session_duration": [3600],
        }
        result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.PASSED)

    def test_success_max_session_duration_1800(self):
        """Role with max_session_duration below 3600 — should pass."""
        resource_conf = {
            "name": ["test_role"],
            "assume_role_policy": ['{"Version":"2012-10-17"}'],
            "max_session_duration": [1800],
        }
        result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.PASSED)

    def test_failure_max_session_duration_7200(self):
        """Role with max_session_duration of 7200 (2 hours) — should fail."""
        resource_conf = {
            "name": ["test_role"],
            "assume_role_policy": ['{"Version":"2012-10-17"}'],
            "max_session_duration": [7200],
        }
        result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_failure_max_session_duration_43200(self):
        """Role with max_session_duration of 43200 (12 hours, AWS max) — should fail."""
        resource_conf = {
            "name": ["test_role"],
            "assume_role_policy": ['{"Version":"2012-10-17"}'],
            "max_session_duration": [43200],
        }
        result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.FAILED)

    def test_unknown_variable_reference(self):
        """Role with max_session_duration as a variable reference — should be UNKNOWN."""
        resource_conf = {
            "name": ["test_role"],
            "assume_role_policy": ['{"Version":"2012-10-17"}'],
            "max_session_duration": ["${var.max_session_duration}"],
        }
        result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(result, CheckResult.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
