import unittest

from checkov.terraform.checks.resource.aws.EKSSecretsEncryption import check
from checkov.common.models.enums import CheckResult


class TestEKSSecretsEncryption(unittest.TestCase):
    def test_failure(self):
        resource_conf = {'name': ['bad-eks'], 'role_arn': ['${var.role_arn}'], 'vpc_config': [{'subnet_ids': [[]], 'endpoint_public_access': [True]}], 'encryption_config': [{'provider': [{'key_arn': ['${var.key_arn}']}], 'resources': [[]]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure2(self):
        resource_conf = {'name': ['bad-eks2'], 'role_arn': ['${var.role_arn}'], 'vpc_config': [{'subnet_ids': [[]], 'endpoint_public_access': [True]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['good-eks2'], 'role_arn': ['${var.role_arn}'], 'vpc_config': [{'subnet_ids': [[]], 'endpoint_public_access': [True]}], 'encryption_config': [{'provider': [{'key_arn': ['${var.key_arn}']}], 'resources': [['secrets']]}]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
