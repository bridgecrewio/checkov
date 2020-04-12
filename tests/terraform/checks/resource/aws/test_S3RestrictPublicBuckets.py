import unittest

from checkov.terraform.checks.resource.aws.S3RestrictPublicBuckets import scanner
from checkov.common.models.enums import CheckResult


class TestS3RestrictPublicBuckets(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'bucket':['foo'], 
                        'block_public_acls': [True], 
                        'block_public_policy': [True],
                        'ignore_public_acls': [True],
                        'restrict_public_buckets': [False]}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'bucket':['foo'], 
                        'block_public_acls': [True], 
                        'block_public_policy': [True],
                        'ignore_public_acls': [True],
                        'restrict_public_buckets': [True]}

        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
