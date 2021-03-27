import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3PublicACLRead import check


class TestS3PublicACL(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_auth_read(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["authenticated-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
