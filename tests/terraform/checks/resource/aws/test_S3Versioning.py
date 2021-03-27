import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3Versioning import scanner


class TestS3Versioning(unittest.TestCase):
    def test_failure_default(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    # key_n checks to demonstrate a partial key match does not cause check to pass
    def test_failure_key_0(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
            "enabled": [True],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_key_1(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
            "wrong_field": [{"enabled": [True]}],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_key_2(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
            "wrong_field": [{"versioning": [{"enabled": [True]}]}],
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
            "versioning": [{"enabled": [True]}],
        }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
