import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.SNSTopicEncryption import check


class TestS3Encryption(unittest.TestCase):
    def test_failure(self):
        resource_conf = {"name": ["terraform-example-sns"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["terraform-example-sns"],
            "kms_master_key_id": ["alias/aws/sqs"],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
