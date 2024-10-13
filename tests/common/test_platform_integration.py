import base64
import os
import random
import unittest
import uuid
from unittest import mock
from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    PolicyMetadataIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.api_url, "foo")

    @staticmethod
    def get_random_string():
        len = random.randrange(5, 50)
        chars = []
        for i in range(0, len):
            chars.append(chr(random.randrange(32, 127)))
        return ''.join(chars)

    def test_is_token_valid(self):
        uuids = []
        for i in range(0, 1000):
            uuids.append(str(uuid.uuid4()))

        # validate BC API keys
        for u in uuids:
            self.assertTrue(BcPlatformIntegration.is_token_valid(u))

        # generate Prisma access keys, which are UUIDs (just reuse the ones from above),
        # and secret keys, which are b64 encoded strings
        for i in range(0, len(uuids)):
            string_to_encode = self.get_random_string()
            encoded = base64.b64encode(bytes(string_to_encode, 'utf-8'))
            uuids[i] = uuids[i] + '::' + encoded.decode('utf-8')

        for u in uuids:
            self.assertTrue(BcPlatformIntegration.is_token_valid(u))

        uuid_str = str(uuid.uuid4())
        b64_str = base64.b64encode(bytes(self.get_random_string(), 'utf-8')).decode('utf-8')
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'{uuid_str}{b64_str}'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'{uuid_str}:{b64_str}'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'{uuid_str}:::{b64_str}'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'{uuid_str}::'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'::{b64_str}'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(''))
        self.assertFalse(BcPlatformIntegration.is_token_valid('1234::56789'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'{uuid_str}::56789'))
        self.assertFalse(BcPlatformIntegration.is_token_valid(f'1234::{b64_str}'))

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
        self.assertEqual(instance.api_url, "https://api0.prismacloud.io/bridgecrew")

    def test_skip_mapping_default(self):
        # Default is False so mapping is obtained
        instance = BcPlatformIntegration()
        instance.api_url = 'https://www.bridgecrew.cloud/v1'
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
        all_checks = BaseCheckRegistry.get_all_registered_checks()
        check_same_severity = next((check for check in all_checks if check.id == "CKV_AWS_15"), None)
        check_different_severity = next((check for check in all_checks if check.id == "CKV_AWS_40"), None)
        check_no_desc_title = next((check for check in all_checks if check.id == "CKV_AWS_53"), None)

        self.assertEqual(check_same_severity.name, 'Ensure IAM password policy requires at least one uppercase letter')
        self.assertEqual(check_same_severity.severity, Severities[BcSeverities.INFO])
        self.assertEqual(check_different_severity.severity, Severities[BcSeverities.CRITICAL])
        self.assertEqual(check_no_desc_title.severity, Severities[BcSeverities.MEDIUM])

    def test_metadata_prisma_key(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000::1234=='
        instance.customer_run_config_response = mock_customer_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        all_checks = BaseCheckRegistry.get_all_registered_checks()
        check_same_severity = next((check for check in all_checks if check.id == "CKV_AWS_15"), None)
        check_different_severity = next((check for check in all_checks if check.id == "CKV_AWS_40"), None)
        check_no_desc_title = next((check for check in all_checks if check.id == "CKV_AWS_53"), None)

        self.assertEqual(check_same_severity.name, 'AWS IAM password policy does not have an uppercase character')
        self.assertEqual(check_different_severity.name, 'AWS IAM policy attached to users')
        self.assertEqual(check_no_desc_title.name, 'Ensure S3 bucket has block public ACLS enabled')
        self.assertEqual(check_same_severity.severity, Severities[BcSeverities.INFO])
        self.assertEqual(check_different_severity.severity, Severities[BcSeverities.HIGH])
        self.assertEqual(check_no_desc_title.severity, None)

    def test_should_upload(self):
        self.assertFalse(get_source_type('vscode').upload_results)
        self.assertTrue(get_source_type('cli').upload_results)
        self.assertTrue(get_source_type('xyz').upload_results)
        self.assertTrue(get_source_type(None).upload_results)

    def test_run_config_url(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'owner/repo'
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000'
        self.assertTrue(instance.get_run_config_url().endswith('/runConfiguration?module=bc&enforcementv2=true&repoId=owner/repo'))
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000::1234=='
        self.assertTrue(instance.get_run_config_url().endswith('/runConfiguration?module=pc&enforcementv2=true&repoId=owner/repo'))
        instance.repo_id = 'encode/më'
        self.assertTrue(instance.get_run_config_url().endswith('/runConfiguration?module=pc&enforcementv2=true&repoId=encode/m%C3%AB'))

    def test_is_valid_policy_filter(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000::1234=='
        instance.customer_run_config_response = mock_customer_run_config()
        self.assertTrue(instance.is_valid_policy_filter(policy_filter=[('policy.label', 'CODE')],
                                                        valid_filters=mock_prisma_policy_filter_response()))
        self.assertFalse(instance.is_valid_policy_filter(policy_filter=[('policy.labels', 'CODE')],
                                                        valid_filters=mock_prisma_policy_filter_response()))
        self.assertFalse(instance.is_valid_policy_filter(policy_filter=[('policy.label', 'CODE'), ('not', 'allowed')],
                                                        valid_filters=mock_prisma_policy_filter_response()))
        self.assertFalse(instance.is_valid_policy_filter(policy_filter=[],
                                                         valid_filters=mock_prisma_policy_filter_response()))
        self.assertFalse(instance.is_valid_policy_filter(policy_filter=[('policy.label', 'A'), ('policy.label', 'B')], valid_filters={}))

    def test_add_static_policy_filters(self):
        self.assertListEqual(BcPlatformIntegration.add_static_policy_filters([]), [('policy.enabled', 'true'), ('policy.subtype', 'build')])
        self.assertListEqual(BcPlatformIntegration.add_static_policy_filters([('policy.enabled', 'true')]), [('policy.enabled', 'true'), ('policy.subtype', 'build')])
        self.assertListEqual(BcPlatformIntegration.add_static_policy_filters([('policy.enabled', 'true'), ('policy.subtype', 'build')]), [('policy.enabled', 'true'), ('policy.subtype', 'build')])
        self.assertListEqual(BcPlatformIntegration.add_static_policy_filters([('policy.label', 'xyz')]), [('policy.label', 'xyz'), ('policy.enabled', 'true'), ('policy.subtype', 'build')])
        self.assertListEqual(BcPlatformIntegration.add_static_policy_filters([('policy.label', 'xyz'), ('policy.enabled', 'true')]), [('policy.label', 'xyz'), ('policy.enabled', 'true'), ('policy.subtype', 'build')])
        self.assertListEqual(BcPlatformIntegration.add_static_policy_filters([('policy.enabled', 'true'), ('policy.label', 'xyz'), ('policy.subtype', 'build')]), [('policy.enabled', 'true'), ('policy.label', 'xyz'), ('policy.subtype', 'build')])

    def test_proxy_without_scheme(self):
        current_proxy = os.environ['https_proxy']
        try:
            os.environ['https_proxy'] = "127.0.0.1"
            instance = BcPlatformIntegration()
            instance.api_url = 'https://www.bridgecrew.cloud/v1'
            instance.setup_http_manager()
        finally:
            os.environ['https_proxy'] = current_proxy

    def test_setup_on_prem(self):
        instance = BcPlatformIntegration()

        instance.customer_run_config_response = None
        instance.setup_on_prem()
        self.assertFalse(instance.on_prem)

        instance.customer_run_config_response = {}
        instance.setup_on_prem()
        self.assertFalse(instance.on_prem)

        instance.customer_run_config_response = {
            'tenantConfig': {}
        }
        instance.setup_on_prem()
        self.assertFalse(instance.on_prem)

        instance.customer_run_config_response = {
            'tenantConfig': {
                'preventCodeUploads': False
            }
        }
        instance.setup_on_prem()
        self.assertFalse(instance.on_prem)

        instance.customer_run_config_response = {
            'tenantConfig': {
                'preventCodeUploads': True
            }
        }
        instance.setup_on_prem()
        self.assertTrue(instance.on_prem)


def mock_customer_run_config():
    return {
        "policyMetadata": {
            "CKV_AWS_15": {
                "id": "BC_AWS_IAM_5",
                "title": "Ensure IAM password policy requires at least one uppercase letter",
                "guideline": "https://docs.bridgecrew.io/docs/iam_5",
                "severity": "INFO",
                "pcSeverity": "INFO",
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


def mock_prisma_policy_filter_response():
    return {
        "policy.name": {
            "options": [
                "CODE1: Ensure subnet is associated with NSG"
            ],
            "staticFilter": False
        },
        "policy.type": {
            "options": [
                "anomaly",
                "audit_event",
                "config",
                "data",
                "network"
            ],
            "staticFilter": True
        },
        "policy.label": {
            "options": [
                "CODE",
                "KARTIK",
                "CRITICAL"
            ],
            "staticFilter": False
        },
        "policy.complianceStandard": {
            "options": [],
            "staticFilter": False
        },
        "policy.complianceRequirement": {
            "options": [],
            "staticFilter": False
        },
        "policy.complianceSection": {
            "options": [],
            "staticFilter": False
        },
        "policy.category": {
            "options": [
                "incident",
                "risk"
            ],
            "staticFilter": True
        },
        "policy.class": {
            "options": [
                "behavioral",
                "exposure",
                "network_protection",
                "privileged_activity_monitoring",
                "vulnerabilities"
            ],
            "staticFilter": True
        },
        "policy.policyMode": {
            "options": [
                "redlock_default",
                "custom"
            ],
            "staticFilter": True
        },
        "policy.subtype": {
            "options": [
                "audit",
                "build",
                "data_classification",
                "dns",
                "malware",
                "network",
                "network_config",
                "network_event",
                "run",
                "run_and_build",
                "ueba"
            ],
            "staticFilter": True
        },
        "policy.enabled": {
            "options": [
                "true",
                "false"
            ],
            "staticFilter": True
        },
        "cloud.type": {
            "options": [
                "alibaba_cloud",
                "aws",
                "azure",
                "gcp",
                "oci"
            ],
            "staticFilter": True
        },
        "policy.severity": {
            "options": [
                "high",
                "medium",
                "low"
            ],
            "staticFilter": True
        },
        "policy.remediable": {
            "options": [
                "true",
                "false"
            ],
            "staticFilter": True
        }
    }


def mock_prisma_policies_response():
    return [
        {
            "policyId": "6960be11-e3a6-46cc-bf66-933c57c2af5d",
            "name": "AWS EBS volume region with encryption is disabled",
            "policyType": "config",
            "policySubTypes": [
                "run",
                "build"
            ],
            "systemDefault": True,
            "policyUpi": "PC-AWS-EC2-778",
            "description": "This policy identifies AWS regions in which new EBS volumes are getting created without any encryption. Encrypting data at rest reduces unintentional exposure of data stored in EBS volumes. It is recommended to configure EBS volume at the regional level so that every new EBS volume created in that region will be enabled with encryption by using a provided encryption key.",
            "severity": "medium",
            "rule": {
                "name": "AWS EBS volume region with encryption is disabled",
                "criteria": "7a951e9f-02d2-4d9f-9441-29b545084585",
                "parameters": {
                    "withIac": "true",
                    "savedSearch": "true"
                },
                "type": "Config",
                "children": [
                    {
                        "criteria": "{\"category\":\"Kubernetes\",\"resourceTypes\":[\"aws_ebs_encryption_by_default\"]}",
                        "type": "build",
                        "metadata": {
                            "checkovId": "CKV_AWS_106"
                        },
                        "recommendation": "Refer the documentation for more details,\nhttps://docs.bridgecrew.io/docs/ensure-kubernetes-secrets-are-encrypted-using-customer-master-keys-cmks-managed-in-aws-kms"
                    }
                ]
            },
            "recommendation": "To enable encryption at region level by default, follow below URL:\nhttps://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html#encryption-by-default\n\nAdditional Information:\n\nTo detect existing EBS volumes that are not encrypted ; refer Saved Search:\nAWS EBS volumes are not encrypted_RL\n\nTo detect existing EBS volumes that are not encrypted with CMK, refer Saved Search:\nAWS EBS volume not encrypted using Customer Managed Key_RL",
            "cloudType": "aws",
            "complianceMetadata": [
                {
                    "standardId": "a0ea1077-424f-45fd-994e-4caef6d4d9de",
                    "standardName": "AWS Foundational Security Best Practices standard",
                    "standardDescription": "AWS Foundational Security Best Practices standard",
                    "requirementId": "Protect",
                    "requirementName": "Protect",
                    "sectionId": "Data protection",
                    "sectionDescription": "Data protection",
                    "policyId": "6960be11-e3a6-46cc-bf66-933c57c2af5d",
                    "complianceId": "2ab6eea3-660b-48c4-a836-53347e702faf",
                    "sectionLabel": "Data protection",
                    "sectionViewOrder": 5,
                    "requirementViewOrder": 2,
                    "systemDefault": True,
                    "customAssigned": False
                }
            ],
            "labels": [
                "CODE",
                "KARTIK"
            ],
            "enabled": True,
            "createdOn": 1634832351154,
            "createdBy": "Prisma Cloud System Admin",
            "lastModifiedOn": 1654106204620,
            "lastModifiedBy": "User",
            "ruleLastModifiedOn": 1639652340813,
            "deleted": False,
            "owner": "Prisma Cloud",
            "policyMode": "redlock_default",
            "policyCategory": "risk",
            "policyClass": "exposure",
            "remediable": False
        },
        {
            "policyId": "c11ce08c-b93e-4e11-8d1c-e5a1339139d1",
            "name": "CUSTOM 3: Ensure subnet is associated with NSG",
            "policyType": "config",
            "policySubTypes": [
                "build"
            ],
            "systemDefault": False,
            "description": "Every subnet should be associated with NSG for controlling access to \nresources within the subnet.\n",
            "severity": "high",
            "rule": {
                "name": "CUSTOM 3: Ensure subnet is associated with NSG",
                "parameters": {
                    "withIac": "true",
                    "savedSearch": "false"
                },
                "type": "Config",
                "children": [
                    {
                        "type": "build",
                        "metadata": {
                            "code": "metadata:\n  name: 'CUSTOM 3: Ensure subnet is associated with NSG'\n  guidelines: \"Every subnet should be associated with NSG for controlling access to\\\n    \\ \\nresources within the subnet.\\n\"\n  category: networking\n  severity: high\nscope:\n  provider: azure\ndefinition:\n  and:\n  - cond_type: connection\n    resource_types:\n    - azurerm_subnet_network_security_group_association\n    connected_resource_types:\n    - azurerm_subnet\n    - azurerm_network_security_group\n    operator: exists\n  - cond_type: filter\n    attribute: resource_type\n    value:\n    - azurerm_subnet\n    operator: within\n"
                        },
                        "recommendation": ""
                    }
                ]
            },
            "recommendation": "",
            "cloudType": "azure",
            "labels": [
                "CODE",
                "KARTIK"
            ],
            "enabled": True,
            "createdOn": 1653999690681,
            "createdBy": "User",
            "lastModifiedOn": 1654065712108,
            "lastModifiedBy": "User",
            "ruleLastModifiedOn": 1653999690681,
            "deleted": False,
            "owner": "Tenant Name",
            "policyMode": "custom",
            "policyCategory": "risk",
            "policyClass": "exposure",
            "remediable": False
        },
        {
            "policyId": "0e4c576e-c934-4af3-8592-a53920e71ffb",
            "name": "CUSTOM POLICY2: Ensure subnet is associated with NSG",
            "policyType": "config",
            "policySubTypes": [
                "build"
            ],
            "systemDefault": False,
            "description": "Every subnet should be associated with NSG for controlling access to \nresources within the subnet.\n",
            "severity": "high",
            "rule": {
                "name": "CUSTOM POLICY2: Ensure subnet is associated with NSG",
                "parameters": {
                    "withIac": "true",
                    "savedSearch": "false"
                },
                "type": "Config",
                "children": [
                    {
                        "type": "build",
                        "metadata": {
                            "code": "metadata:\n  name: 'CUSTOM POLICY2: Ensure subnet is associated with NSG'\n  guidelines: \"Every subnet should be associated with NSG for controlling access to\\\n    \\ \\nresources within the subnet.\\n\"\n  category: networking\n  severity: high\nscope:\n  provider: azure\ndefinition:\n  and:\n  - cond_type: connection\n    resource_types:\n    - azurerm_subnet_network_security_group_association\n    connected_resource_types:\n    - azurerm_subnet\n    - azurerm_network_security_group\n    operator: exists\n  - cond_type: filter\n    attribute: resource_type\n    value:\n    - azurerm_subnet\n    operator: within\n"
                        },
                        "recommendation": ""
                    }
                ]
            },
            "recommendation": "",
            "cloudType": "azure",
            "labels": [
                "CODE",
                "KARTIK"
            ],
            "enabled": True,
            "createdOn": 1653003961960,
            "createdBy": "User",
            "lastModifiedOn": 1653003961960,
            "lastModifiedBy": "User",
            "ruleLastModifiedOn": 1653003961960,
            "deleted": False,
            "owner": "Tenant Name",
            "policyMode": "custom",
            "policyCategory": "risk",
            "policyClass": "exposure",
            "remediable": False
        },
        {
            "policyId": "e4080750-1b9a-4b7b-9acf-7057c61eaa9d",
            "name": "Check that all encrypted RDS clusters are tagged with encrypted: True",
            "policyType": "config",
            "policySubTypes": [
                "build"
            ],
            "systemDefault": False,
            "description": "Check that all encrypted RDS clusters are tagged with encrypted: True",
            "severity": "high",
            "rule": {
                "name": "Check that all encrypted RDS clusters are tagged with encrypted: True",
                "parameters": {
                    "withIac": "true",
                    "savedSearch": "false"
                },
                "type": "Config",
                "children": [
                    {
                        "type": "build",
                        "metadata": {
                            "code": "---\nmetadata:\n name: \"Check that all encrypted RDS clusters are tagged with encrypted: True\"\n guidelines: \"Tags Governance - in case of the matched condition below -> add/modify a tag of encrypted:true\"\n category: \"secrets\"\n severity: \"high\"\nscope:\n  provider: \"aws\"\ndefinition:\n and:\n     - cond_type: \"attribute\"\n       resource_types:\n       - \"aws_rds_cluster\"\n       attribute: \"tags.encrypted\"\n       operator: \"equals\"\n       value: \"true\"\n     - or:\n         - cond_type: \"attribute\"\n           resource_types:\n           - \"aws_rds_cluster\"\n           attribute: \"kms_key_id\"\n           operator: \"exists\"\n         - cond_type: \"attribute\"\n           resource_types:\n           - \"aws_rds_cluster\"\n           attribute: \"storage_encrypted\"\n           operator: \"equals\"\n           value: \"true\""
                        },
                        "recommendation": ""
                    }
                ]
            },
            "recommendation": "",
            "cloudType": "aws",
            "labels": [
                "CODE",
                "KARTIK"
            ],
            "enabled": True,
            "createdOn": 1653999052972,
            "createdBy": "User",
            "lastModifiedOn": 1653999052972,
            "lastModifiedBy": "User",
            "ruleLastModifiedOn": 1653999052972,
            "deleted": False,
            "owner": "Tenant Name",
            "policyMode": "custom",
            "policyCategory": "risk",
            "policyClass": "exposure",
            "remediable": False
        }
    ]


if __name__ == '__main__':
    unittest.main()
