import json
import os
import unittest

from checkov.common.bridgecrew.integration_features.features.attribute_resource_types_integration import \
    AttributeResourceTypesIntegration, integration as attribute_resource_types_integration
from checkov.common.bridgecrew.integration_features.features.custom_policies_integration import \
    CustomPoliciesIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry, get_graph_checks_registry
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.terraform.runner import Runner as TerraformRunner
from checkov.cloudformation.runner import Runner as CFNRunner
from checkov.runner_filter import RunnerFilter
from pathlib import Path


class TestAttributeResourceTypeIntegration(unittest.TestCase):
    def tearDown(self) -> None:
        get_graph_checks_registry("terraform").checks = []

    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True

        attr_res_integration = AttributeResourceTypesIntegration(instance)

        self.assertTrue(attr_res_integration.is_valid())

        instance.skip_download = True
        self.assertFalse(attr_res_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(attr_res_integration.is_valid())

        instance.skip_download = False
        self.assertFalse(attr_res_integration.is_valid())

        attr_res_integration.integration_feature_failures = True
        self.assertFalse(attr_res_integration.is_valid())

    def test_get_attribute_resource_types(self):
        attr_res_integration = AttributeResourceTypesIntegration(bc_integration)
        attr_res_integration.attribute_resources = mock_attribute_resource_definitions()
        # resource
        self.assertIsNone(attr_res_integration.get_attribute_resource_types({}))
        self.assertIsNone(attr_res_integration.get_attribute_resource_types({'attribute': 'abc'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'labels'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'tags'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'Tags'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'tags.owner'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'labels.owner'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'Tags.Key'}))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'labels'}, provider='gcp'))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'tags'}, provider='aws'))
        self.assertIsNotNone(
            attr_res_integration.get_attribute_resource_types({'attribute': 'tags'}, provider='alibabacloud'))
        self.assertIsNotNone(attr_res_integration.get_attribute_resource_types({'attribute': 'Tags'}, provider='aws'))
        self.assertIsNone(attr_res_integration.get_attribute_resource_types({'attribute': 'labels'}, provider='aws'))
        self.assertIsNone(attr_res_integration.get_attribute_resource_types({'attribute': 'tags'}, provider='gcp'))
        self.assertIsNone(attr_res_integration.get_attribute_resource_types({'attribute': 'Tags'}, provider='gcp'))
        self.assertTrue(
            any(r.startswith('aws') for r in attr_res_integration.get_attribute_resource_types({'attribute': 'tags'})))
        self.assertTrue(any(r.startswith('aws') for r in
                            attr_res_integration.get_attribute_resource_types({'attribute': 'tags'}, provider='aws')))

        # alicloud is the resource type prefix, but alibabacloud is the name of the custom policy provider, so this is intentional
        self.assertFalse(any(r.startswith('alicloud') for r in
                             attr_res_integration.get_attribute_resource_types({'attribute': 'tags'}, provider='aws')))
        self.assertTrue(any(
            r.startswith('alicloud') for r in attr_res_integration.get_attribute_resource_types({'attribute': 'tags'})))
        self.assertTrue(any(r.startswith('alicloud') for r in
                            attr_res_integration.get_attribute_resource_types({'attribute': 'tags'},
                                                                              provider='alibabacloud')))
        self.assertFalse(any(r.startswith('aws') for r in
                             attr_res_integration.get_attribute_resource_types({'attribute': 'tags'},
                                                                               provider='alibabacloud')))

    def test_build_resource_definitions(self):
        attr_res_integration = AttributeResourceTypesIntegration(bc_integration)
        attr_res_integration._build_attribute_resource_map(mock_resource_definition_response())

        # do equality check as set
        attribute_resources = {
            attribute: {
                provider: set(resources) for provider, resources in provider_map.items()
            } for attribute, provider_map in attr_res_integration.attribute_resources.items()
        }

        expected = {
            'tags': {
                'aws': {'aws_s3_bucket'},
                'azure': {'azurerm_storage_account'},
                'alibabacloud': {'alicloud_adb_db_cluster'},
                '__all__': {'alicloud_adb_db_cluster', 'aws_s3_bucket', 'azurerm_storage_account'}
            },
            'Tags': {
                'aws': {'AWS::S3::Bucket'},
                '__all__': {'AWS::S3::Bucket'}
            },
            'labels': {
                'gcp': {'google_bigquery_dataset'},
                '__all__': {'google_bigquery_dataset'}
            }
        }
        self.assertEqual(attribute_resources, expected)

    def test_scan_with_attribute(self):
        temp_integration = BcPlatformIntegration()
        attribute_resource_types_integration.bc_integration = temp_integration
        temp_integration.platform_integration_configured = True
        temp_integration.customer_run_config_response = mock_customer_run_config()

        attribute_resource_types_integration.pre_scan()

        # for this test, we simulate some of the check registry manipulation; otherwise the singleton
        # instance will be modified and break other tests.

        parser = NXGraphCheckParser()

        registry = Registry(parser=NXGraphCheckParser(), checks_dir=str(
            Path(__file__).parent.parent.parent.parent / "checkov" / "terraform" / "checks" / "graph_checks"))
        checks = [parser.parse_raw_check(CustomPoliciesIntegration._convert_raw_check(p)) for p in temp_integration.customer_run_config_response['customPolicies']]
        registry.checks = checks  # simulate that the policy downloader will do

        tf_runner = TerraformRunner(external_registries=[registry])
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/resources"

        report = tf_runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=['policy_id_1']))

        # we only expect the aws_s3_bucket to fail, because the mock response does not include aws_subnet as a taggable resource
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.failed_checks[0].check_id, 'policy_id_1')
        self.assertEqual(report.failed_checks[0].resource, 'aws_s3_bucket.b')

        attribute_resource_types_integration.bc_integration = bc_integration
        attribute_resource_types_integration.attribute_resources = {}


def mock_attribute_resource_definitions():
    return {
        'tags': {
            'aws': ['aws_s3_bucket'],
            'alibabacloud': ['alicloud_adb_db_cluster'],
            '__all__': ['aws_s3_bucket', 'alicloud_adb_db_cluster']
        },
        'Tags': {
            'aws': ['AWS::S3::Bucket'],
            '__all__': ['AWS::S3::Bucket']
        },
        'labels': {
            'gcp': ['google_bigquery_dataset'],
            '__all__': ['google_bigquery_dataset']
        }
    }


def mock_resource_definition_response():
    return {
        "resourceTypes": {
            "aws": {
                "provider": "AWS",
                "text": "AWS Terraform Provider",
                "arguments": []
            },
            "aws_s3_bucket": {
                "provider": "AWS",
                "text": "S3 Bucket",
                "arguments": [
                    "acceleration_status",
                    "acl",
                    "tags",
                    "tags_all"
                ]
            },
            "aws_security_group_rule": {
                "provider": "AWS",
                "text": "Security Group Rule",
                "arguments": [
                    "cidr_blocks",
                    "description",
                    "from_port",
                    "to_port"
                ]
            },
            "azurerm_storage_account": {
                "provider": "Azure",
                "text": "Storage Account",
                "arguments": [
                    "access_tier",
                    "account_kind",
                    "account_replication_type",
                    "account_tier",
                    "allow_blob_public_access",
                    "tags"
                ]
            },
            "azurerm_lb_rule": {
                "provider": "Azure",
                "text": "ALB Rule",
                "arguments": [
                    "backend_address_pool_ids",
                    "backend_port",
                    "disable_outbound_snat"
                ]
            },
            "alicloud_adb_db_cluster": {
                "provider": "ALI",
                "text": "Adb DB Cluster",
                "arguments": [
                    "auto_renew_period",
                    "compute_resource",
                    "connection_string",
                    "tags"
                ]
            },
            "alicloud_alb_rule": {
                "provider": "ALI",
                "text": "ALB Rule",
                "arguments": [
                    "dry_run",
                    "id",
                    "listener_id",
                    "priority"
                ]
            },
            "google_bigquery_dataset": {
                "provider": "GCP",
                "text": "Bigquery Dataset",
                "arguments": [
                    "access.dataset.dataset.dataset_id",
                    "access.dataset.dataset.project_id",
                    "access.dataset.target_types",
                    "access.domain",
                    "labels"
                ],
                "prismaResourceTypeId": 20002
            },
            "google_app_engine_firewall_rule": {
                "provider": "GCP",
                "text": "App Engine Firewall Rule",
                "arguments": [
                    "action",
                    "description",
                    "id",
                    "priority",
                    "project"
                ],
                "prismaResourceTypeId": 20020
            },
            "AWS::S3::Bucket": {
                "provider": "AWS",
                "text": "S3 Bucket",
                "arguments": [
                    "AccelerateConfiguration.AccelerationStatus",
                    "AccessControl",
                    "Tags.Key",
                    "Tags.Value",
                    "VersioningConfiguration.Status"
                ]
            },
            "AWS::Macie::Session": {
                "provider": "AWS",
                "text": "Macie Session",
                "arguments": [
                    "FindingPublishingFrequency",
                    "Status"
                ]
            }
        },
        "filterAttributes": {
            "tags": [
                "aws",
                "azure",
                'alibabacloud'
            ],
            "labels": [
                "gcp"
            ],
            "Tags": [
                "aws"
            ]
        }
    }


def mock_customer_run_config():
    return {
        "customPolicies": [
            {
                "id": "policy_id_1",
                "title": "yaml1",
                "severity": "MEDIUM",
                "category": "General",
                "guideline": "yaml1",
                "code": json.dumps({
                    "or": [
                        {
                            "value": "xyz",
                            "operator": "contains",
                            "attribute": "tags",
                            "cond_type": "attribute",
                            "resource_types": [
                                "all"
                            ]
                        }
                    ]
                }),
                "benchmarks": {},
            }
        ],
        "resourceDefinitions": mock_resource_definition_response()
    }


if __name__ == '__main__':
    unittest.main()
