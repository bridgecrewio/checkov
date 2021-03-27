import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.CodeBuildProjectEncryption import check


class TestCodeBuildProjectEncryption(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": "test-project",
            "artifacts": [
                {
                    "type": "S3",
                    "encryption_disabled": True,
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success_type_no_artifacts_encryption_ignored(self):
        resource_conf = {
            "name": "test-project",
            "artifacts": [
                {
                    "type": "NO_ARTIFACTS",
                    "encryption_disabled": True,
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_encryption_disabled(self):
        resource_conf = {
            "name": "test-project",
            "artifacts": [
                {
                    "type": "S3",
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": "test-project",
            "artifacts": [
                {
                    "type": "S3",
                    "encryption_disabled": False,
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
