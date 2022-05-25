import os
import unittest
from unittest import mock
from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    PolicyMetadataIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.terraform.checks.resource.registry import resource_registry as tf_registry


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.api_url, "foo")

    def test_overriding_pc_api_url(self):
        instance = BcPlatformIntegration()
        instance.setup_bridgecrew_credentials(
            repo_id="bridgecrewio/checkov",
            prisma_api_url="https://api0.prismacloud.io",
            source=get_source_type('disabled')
        )
        self.assertEqual(instance.api_url, "https://api0.prismacloud.io/bridgecrew")
        self.assertEqual(instance.prisma_api_url, "https://api0.prismacloud.io")

    def test_no_overriding_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.api_url, "https://www.bridgecrew.cloud")

    def test_skip_mapping_default(self):
        # Default is False so mapping is obtained
        instance = BcPlatformIntegration()
        instance.setup_http_manager()
        instance.get_public_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        self.assertIsNotNone(metadata_integration.check_metadata)
        self.assertGreater(len(metadata_integration.check_metadata), 0)

    def test_skip_mapping_true(self):
        instance = BcPlatformIntegration()
        instance.skip_download = True
        instance.setup_http_manager()
        instance.get_public_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        self.assertIsNotNone(metadata_integration.check_metadata)
        self.assertDictEqual({}, metadata_integration.check_metadata)

    def test_metadata_bc_key(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000'
        instance.customer_run_config_response = mock_customer_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        check_same_severity = tf_registry.get_check_by_id('CKV_AWS_15')
        check_different_severity = tf_registry.get_check_by_id('CKV_AWS_40')
        check_no_desc_title = tf_registry.get_check_by_id('CKV_AWS_53')

        self.assertEqual(check_same_severity.name, 'Ensure IAM password policy requires at least one uppercase letter')
        self.assertEqual(check_same_severity.severity, Severities[BcSeverities.MEDIUM])
        self.assertEqual(check_different_severity.severity, Severities[BcSeverities.CRITICAL])
        self.assertEqual(check_no_desc_title.severity, Severities[BcSeverities.MEDIUM])

    def test_metadata_prisma_key(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000::1234=='
        instance.customer_run_config_response = mock_customer_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        check_same_severity = tf_registry.get_check_by_id('CKV_AWS_15')
        check_different_severity = tf_registry.get_check_by_id('CKV_AWS_40')
        check_no_desc_title = tf_registry.get_check_by_id('CKV_AWS_53')

        self.assertEqual(check_same_severity.name, 'AWS IAM password policy does not have an uppercase character')
        self.assertEqual(check_different_severity.name, 'AWS IAM policy attached to users')
        self.assertEqual(check_no_desc_title.name, 'Ensure S3 bucket has block public ACLS enabled')
        self.assertEqual(check_same_severity.severity, Severities[BcSeverities.MEDIUM])
        self.assertEqual(check_different_severity.severity, Severities[BcSeverities.HIGH])
        self.assertEqual(check_different_severity.severity, Severities[BcSeverities.HIGH])

    def test_should_upload(self):
        self.assertFalse(get_source_type('vscode').upload_results)
        self.assertTrue(get_source_type('cli').upload_results)
        self.assertTrue(get_source_type('xyz').upload_results)
        self.assertTrue(get_source_type(None).upload_results)

    def test_run_config_url(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000'
        self.assertTrue(instance.get_run_config_url().endswith('/runConfiguration?module=bc'))
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000::1234=='
        self.assertTrue(instance.get_run_config_url().endswith('/runConfiguration?module=pc'))


def mock_customer_run_config():
    return {
        "policyMetadata": {
            "CKV_AWS_15": {
                "id": "BC_AWS_IAM_5",
                "title": "Ensure IAM password policy requires at least one uppercase letter",
                "guideline": "https://docs.bridgecrew.io/docs/iam_5",
                "severity": "MEDIUM",
                "pcSeverity": "MEDIUM",
                "category": "IAM",
                "checkovId": "CKV_AWS_15",
                "constructiveTitle": "Ensure AWS IAM password policy has an uppercase character",
                "descriptiveTitle": "AWS IAM password policy does not have an uppercase character",
                "pcPolicyId": "31626ca9-f659-4d25-9d88-fa32262bbba7",
                "additionalPcPolicyIds": [
                    "31626ca9-f659-4d25-9d88-fa32262bbba7"
                ],
                "benchmarks": {}
            },
            "CKV_AWS_40": {
                "id": "BC_AWS_IAM_16",
                "title": "Ensure IAM policies are attached only to groups or roles",
                "guideline": "https://docs.bridgecrew.io/docs/iam_16-iam-policy-privileges-1",
                "severity": "CRITICAL",
                "pcSeverity": "HIGH",
                "category": "IAM",
                "checkovId": "CKV_AWS_40",
                "constructiveTitle": "Ensure IAM policies are only attached to Groups and Roles",
                "descriptiveTitle": "AWS IAM policy attached to users",
                "pcPolicyId": "2b7e07ba-56c8-42db-8db4-a4b65f5066c4",
                "additionalPcPolicyIds": [
                    "2b7e07ba-56c8-42db-8db4-a4b65f5066c4"
                ],
                "benchmarks": {}
            },
            "CKV_AWS_53": {
                "id": "BC_AWS_S3_19",
                "title": "Ensure S3 bucket has block public ACLS enabled",
                "guideline": "https://docs.bridgecrew.io/docs/bc_aws_s3_19",
                "severity": "MEDIUM",
                "pcSeverity": None,
                "category": "Storage",
                "checkovId": "CKV_AWS_53",
                "constructiveTitle": "Ensure S3 bucket has block public ACLS enabled",
                "descriptiveTitle": None,
                "pcPolicyId": "34064d53-1fd1-42e6-b075-45dce495caca",
                "additionalPcPolicyIds": [
                    "34064d53-1fd1-42e6-b075-45dce495caca"
                ],
                "benchmarks": {}
            }
        }
    }


if __name__ == '__main__':
    unittest.main()
