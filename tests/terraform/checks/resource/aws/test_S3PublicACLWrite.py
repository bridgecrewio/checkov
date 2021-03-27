import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.S3PublicACLWRITE import check


class TestS3PublicACLWrite(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read-write"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "region": ["us-west-2"],
            "bucket": ["my_bucket"],
            "acl": ["public-read"],
            "force_destroy": [True],
            "tags": [{"Name": "my-bucket"}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success2(self):
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
