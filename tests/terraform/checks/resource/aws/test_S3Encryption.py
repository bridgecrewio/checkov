import unittest

from checkov.terraform.checks.resource.aws.S3Encryption import check
from checkov.terraform.models.enums import CheckResult


class TestS3Encryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {"region": ["us-west-2"],
                         "bucket": ["my_bucket"],
                         "acl": ["public-read"],
                         "force_destroy": [True],
                         "tags": [{"Name": "my-bucket"}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {"region": ["us-west-2"],
                         "bucket": ["my_bucket"],
                         "acl": ["public-read"],
                         "force_destroy": [True],
                         "tags": [{"Name": "my-bucket"}],
                         "logging": [{"target_bucket": "logging-bucket",
                                      "target_prefix": "log/"
                                      }],
                         "server_side_encryption_configuration": [
                             {"rule": [{"apply_server_side_encryption_by_default": [{
                                 "kms_master_key_id": "foo",
                                 "sse_algorithm": "aws:kms"
                             }]}]}]
                         }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
