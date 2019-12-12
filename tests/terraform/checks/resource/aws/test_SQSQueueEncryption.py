import unittest

from checkov.terraform.checks.resource.aws.SQSQueueEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestS3Encryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['terraform-example-queue']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['terraform-example-queue'], 'kms_master_key_id': ['alias/aws/sqs'],
                         'kms_data_key_reuse_period_seconds': [300]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
