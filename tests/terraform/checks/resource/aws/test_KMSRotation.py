import unittest

from checkov.terraform.checks.resource.aws.KMSRotation import check
from checkov.terraform.models.enums import CheckResult


class TestKMSRotation(unittest.TestCase):

    def test_success(self):
        resource_conf = {
            "description": "KMS key 1",
            "deletion_window_in_days": 10,
            "enable_key_rotation": True
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        resource_conf = {
            "description": "KMS key 1",
            "deletion_window_in_days": 10,
            "enable_key_rotation": False
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_on_missing_property(self):
        resource_conf = {
            "description": "KMS key 1",
            "deletion_window_in_days": 10,
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
