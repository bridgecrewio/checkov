import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.KinesisStreamEncryptionType import check


class TestKinesisStreamEncryptionType(unittest.TestCase):
    def test_failure(self):
        resource_conf = {
            "name": ["terraform-kinesis-test"],
            "shard_count": [1],
            "retention_period": [48],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": ["terraform-kinesis-test"],
            "shard_count": [1],
            "retention_period": [48],
            "encryption_type": ["KMS"],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == "__main__":
    unittest.main()
