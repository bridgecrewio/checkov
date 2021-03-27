import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3MFADelete import scanner


class TestS3MFADelete(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_versioning_enabled(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
            "versioning": [{"enabled": [True]}],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
            "logging": [{"target_bucket": "logging-bucket", "target_prefix": "log/"}],
            "versioning": [{"enabled": [True]}, {"mfa_delete": [True]}],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
