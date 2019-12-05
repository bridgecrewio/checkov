import unittest

from checkov.terraform.models.enums import ScanResult
from checkov.terraform.checks.resource.aws.SNSTopicEncryption import scanner


class TestS3Encryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['terraform-example-sns']}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf = {'name': ['terraform-example-sns'], 'kms_master_key_id': ['alias/aws/sqs'],
                       }
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
