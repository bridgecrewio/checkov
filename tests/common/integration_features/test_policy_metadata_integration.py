import unittest

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    PolicyMetadataIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration



class TestPolicyMetadataIntegration(unittest.TestCase):

    def test_filtered_policy_ids(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '00000000-0000-0000-0000-000000000000::1234=='
        instance.customer_run_config_response = mock_customer_run_config()
        instance.prisma_policies_response = mock_prisma_policies_response()
        instance.prisma_policies_exception_response = [mock_prisma_policies_response()[0]]
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        metadata_integration.pc_to_ckv_id_mapping
        self.assertDictEqual(metadata_integration.pc_to_ckv_id_mapping, {'6960be11-e3a6-46cc-bf66-933c57c2af5d': 'CKV_AWS_212', '3dc2478c-bf25-4383-aaa1-30feb5cda586': '806079891421835264_AZR_1685557908904', 'c11ce08c-b93e-4e11-8d1c-e5a1339139d1': 'CKV_AWS_40', '0e4c576e-c934-4af3-8592-a53920e71ffb': 'CKV_AWS_53', '1234': 'CKV3_SAST_123'})
        self.assertListEqual(metadata_integration.filtered_policy_ids, ['CKV_AWS_212', '806079891421835264_AZR_1685557908904', 'CKV_AWS_40', 'CKV_AWS_53', 'CKV_AZURE_122'])
        self.assertListEqual(metadata_integration.filtered_exception_policy_ids, ['CKV_AWS_212'])
        self.assertSetEqual(set(metadata_integration.sast_check_metadata.keys()), {'CKV3_SAST_123'})


def mock_customer_run_config():
    return {
        "policyMetadata": {
            "CKV_AWS_212": {
                "id": "BC_AWS_IAM_5",
                "title": "Ensure IAM password policy requires at least one uppercase letter",
                "guideline": "https://docs.bridgecrew.io/docs/iam_5",
                "severity": "MEDIUM",
                "pcSeverity": "MEDIUM",
                "category": "IAM",
                "checkovId": "CKV_AWS_212",
                "constructiveTitle": "Ensure AWS IAM password policy has an uppercase character",
                "descriptiveTitle": "AWS IAM password policy does not have an uppercase character",
                "pcPolicyId": "6960be11-e3a6-46cc-bf66-933c57c2af5d",
                "additionalPcPolicyIds": [
                    "6960be11-e3a6-46cc-bf66-933c57c2af5d"
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
                "pcPolicyId": "c11ce08c-b93e-4e11-8d1c-e5a1339139d1",
                "additionalPcPolicyIds": [
                    "c11ce08c-b93e-4e11-8d1c-e5a1339139d1"
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
                "pcPolicyId": "0e4c576e-c934-4af3-8592-a53920e71ffb",
                "additionalPcPolicyIds": [
                    "0e4c576e-c934-4af3-8592-a53920e71ffb"
                ],
                "benchmarks": {}
            },
            "CKV_AZURE_122": {
                "id": "BC_AZR_NETWORKING_39",
                "title": "Ensure that Application Gateway uses WAF in \"Detection\" or \"Prevention\" modes",
                "guideline": "https://docs.bridgecrew.io/docs/ensure-that-application-gateway-uses-waf-in-detection-or-prevention-modes",
                "severity": "LOW",
                "pcSeverity": "LOW",
                "category": "Networking",
                "checkovId": "CKV_AZURE_122",
                "constructiveTitle": "Ensure application gateway uses WAF in Detection or Prevention modes",
                "descriptiveTitle": "Application gateway does not use WAF in Detection or Prevention modes",
                "pcPolicyId": "3dc2478c-bf25-4383-aaa1-30feb5cda586",
                "additionalPcPolicyIds": [
                    "3dc2478c-bf25-4383-aaa1-30feb5cda586"
                ],
                "benchmarks": {}
            },
            "CKV3_SAST_123": {
                "id": "BC_SAST_123",
                "title": "sast",
                "guideline": "https://docs.bridgecrew.io/docs/abc",
                "severity": "LOW",
                "pcSeverity": "LOW",
                "category": "Networking",
                "checkovId": "CKV3_SAST_123",
                "constructiveTitle": "sast",
                "descriptiveTitle": "sast",
                "pcPolicyId": "1234",
                "additionalPcPolicyIds": [
                    "1234"
                ],
                "benchmarks": {}
            }
        },
        "customPolicies": [
            {
            "id": "806079891421835264_AZR_1685557908904",
            "code": "null",
            "title": "Application gateway does not use WAF in Detection or Prevention modes",
            "guideline": "Refer the documentation for more details,\nhttps://docs.bridgecrew.io/docs/ensure-that-application-gateway-uses-waf-in-detection-or-prevention-modes",
            "severity": "MEDIUM",
            "pcSeverity": "MEDIUM",
            "category": "Networking",
            "pcPolicyId": "3dc2478c-bf25-4383-aaa1-30feb5cda586",
            "additionalPcPolicyIds": [
                "3dc2478c-bf25-4383-aaa1-30feb5cda586"
            ],
            "sourceIncidentId": "BC_AZR_NETWORKING_39",
            "benchmarks": {},
            "frameworks": [
                "CloudFormation",
                "Terraform"
            ],
            "provider": "Azure"
            }
        ]
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
            "policyId": "3dc2478c-bf25-4383-aaa1-30feb5cda586",
            "name": "Application gateway does not use WAF in Detection or Prevention modes",
            "policyType": "config",
            "policySubTypes": [
                "build"
            ],
            "systemDefault": True,
            "description": "Ensure that Application Gateway uses WAF in \"Detection\" or \"Prevention\" modes",
            "severity": "medium",
            "rule": {
                "parameters": {
                    "withIac": "true",
                    "savedSearch": "false"
                },
                "type": "Config",
                "children": [
                    {
                        "criteria": "{\"category\":\"Networking\",\"resourceTypes\":[\"azurerm_web_application_firewall_policy\"]}",
                        "type": "build",
                        "metadata": {
                            "checkovId": "CKV_AZURE_122"
                        },
                        "recommendation": "Refer the documentation for more details,\nhttps://docs.bridgecrew.io/docs/ensure-that-application-gateway-uses-waf-in-detection-or-prevention-modes"
                    }
                ]
            },
            "recommendation": "",
            "cloudType": "azure",
            "labels": [
                "pcsup"
            ],
            "enabled": True,
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
    ]


if __name__ == '__main__':
    unittest.main()
