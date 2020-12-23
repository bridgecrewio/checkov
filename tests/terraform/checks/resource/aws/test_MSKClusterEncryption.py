import unittest

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.aws.MSKClusterEncryption import check


class TestMSKClusterEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {
            "name": "test-project",
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_non_tls(self):
        resource_conf = {
            "name": "test-project",
            "encryption_info": [
                {
                    "encryption_at_rest_kms_key_arn": "aws_kms_key.kms.arn",
                    "encryption_in_transit": [
                        {
                            "client_broker": ["PLAINTEXT"],
                            "in_cluster": ["true"],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_in_cluster(self):
        resource_conf = {
            "name": "test-project",
            "encryption_info": [
                {
                    "encryption_at_rest_kms_key_arn": ["aws_kms_key.kms.arn"],
                    "encryption_in_transit": [
                        {
                            "client_broker": ["TLS"],
                            "in_cluster": [False],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {
            "name": "test-project",
            "encryption_info": [
                {
                    "encryption_at_rest_kms_key_arn": ["aws_kms_key.kms.arn"],
                    "encryption_in_transit": [
                        {
                            "client_broker": ["TLS"],
                            "in_cluster": ["true"],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_success_no_encrypt_block(self):
        resource_conf = {
            "name": "test-project",
            "encryption_info": [
                {
                    "encryption_at_rest_kms_key_arn": ["aws_kms_key.kms.arn"],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    # Regression test for https://github.com/bridgecrewio/checkov/issues/747
    def test_success_no_encryption_at_rest_kms_key_arn_specified(self):
        resource_conf = {
            "name": "test-project",
            "encryption_info": [{}],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    # Regression test for https://github.com/bridgecrewio/checkov/issues/747
    def test_success_encryption_in_transit_and_no_encryption_at_rest_kms_key_arn_specified(self):
        resource_conf = {
            "name": "test-project",
            "encryption_info": [
                {
                    "encryption_in_transit": [
                        {
                            "client_broker": ["TLS"],
                            "in_cluster": [True],
                        }
                    ],
                }
            ],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
