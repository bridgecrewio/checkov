import json
import os
import unittest
from copy import deepcopy

from checkov.common.bridgecrew.integration_features.features.custom_policies_integration import \
    CustomPoliciesIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry, get_all_graph_checks_registries, get_graph_checks_registry
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.terraform.runner import Runner as TerraformRunner
from checkov.cloudformation.runner import Runner as CFNRunner
from checkov.runner_filter import RunnerFilter
from pathlib import Path


class TestCustomPoliciesIntegration(unittest.TestCase):
    def tearDown(self) -> None:
        get_graph_checks_registry("cloudformation").checks = []
        get_graph_checks_registry("terraform").checks = []
        get_graph_checks_registry("kubernetes").checks = []
        get_graph_checks_registry("bicep").checks = []

    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True

        custom_policies_integration = CustomPoliciesIntegration(instance)

        self.assertTrue(custom_policies_integration.is_valid())

        instance.skip_download = True
        self.assertFalse(custom_policies_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(custom_policies_integration.is_valid())

        instance.skip_download = False
        self.assertFalse(custom_policies_integration.is_valid())

        custom_policies_integration.integration_feature_failures = True
        self.assertFalse(custom_policies_integration.is_valid())

    def test_policy_load(self):
        # response from API
        policies = [
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
                            "operator": "equals",
                            "attribute": "xyz",
                            "cond_type": "attribute",
                            "resource_types": [
                                "aws_s3_bucket"
                            ]
                        }
                    ]
                }),
                "benchmarks": {},
            },
            {
                "id": "policy_id_2",
                "title": "ui1",
                "severity": "HIGH",
                "category": "General",
                "guideline": "ui1",
                "code": json.dumps({
                    "value": "abc",
                    "operator": "equals",
                    "attribute": "region",
                    "cond_type": "attribute",
                    "resource_types": [
                        "aws_s3_bucket"
                    ]
                }),
                "benchmarks": {},
            },
            {
                "id": "policy_id_3",
                "title": "Check that all EC2 instances are tagged with yor_trace",
                "descriptiveTitle": "null",
                "constructiveTitle": "null",
                "severity": "LOW",
                "pcSeverity": "null",
                "category": "General",
                "guideline": "Check for YOR tagging",
                "code": json.dumps({
                    "operator": "exists",
                    "attribute": "Tags.yor_trace",
                    "cond_type": "attribute",
                    "resource_types": [
                        "AWS::EC2::Instance"
                    ]
                }),
                "benchmarks": {},
                "frameworks": [
                    "Terraform",
                    "CloudFormation"
                ],
            },
            {
                "id": "policy_id_4",
                "title": "Custom - ensure MSK Cluster logging is enabled",
                "descriptiveTitle": "null",
                "constructiveTitle": "null",
                "severity": "MEDIUM",
                "pcSeverity": "null",
                "category": "Logging",
                "resourceTypes": [
                    "AWS::MSK::Cluster"
                ],
                "accountsData": {},
                "guideline": "Some sample guidelines",
                "isCustom": True,
                "code": json.dumps({
                    "or": [
                        {
                            "value": "true",
                            "operator": "equals",
                            "attribute": "LoggingInfo.BrokerLogs.S3.Enabled",
                            "cond_type": "attribute",
                            "resource_types": [
                                "AWS::MSK::Cluster"
                            ]
                        },
                        {
                            "value": "true",
                            "operator": "equals",
                            "attribute": "LoggingInfo.BrokerLogs.Firehose.Enabled",
                            "cond_type": "attribute",
                            "resource_types": [
                                "AWS::MSK::Cluster"
                            ]
                        },
                        {
                            "value": "true",
                            "operator": "equals",
                            "attribute": "LoggingInfo.BrokerLogs.CloudWatchLogs.Enabled",
                            "cond_type": "attribute",
                            "resource_types": [
                                "AWS::MSK::Cluster"
                            ]
                        }
                    ]
                }),
                "benchmarks": {},
                "frameworks": [
                    "Terraform",
                    "CloudFormation"
                ],
            }
        ]

        # for this test, we simulate some of the check registry manipulation; otherwise the singleton
        # instance will be modified and break other tests.

        parser = GraphCheckParser()

        registry = Registry(parser=GraphCheckParser(), checks_dir=str(
            Path(__file__).parent.parent.parent.parent / "checkov" / "terraform" / "checks" / "graph_checks"))
        checks = [parser.parse_raw_check(CustomPoliciesIntegration._convert_raw_check(p)) for p in policies]
        registry.checks = checks  # simulate that the policy downloader will do

        tf_runner = TerraformRunner(external_registries=[registry])
        cfn_runner = CFNRunner(external_registries=[registry])
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_custom_policy_dir"

        report = tf_runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter())
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_2']), 1)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_1']), 1)

        report = tf_runner.run(root_folder=test_files_dir,
                               runner_filter=RunnerFilter(checks=['policy_id_2']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_2']), 1)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_1']), 0)

        report = tf_runner.run(root_folder=test_files_dir,
                               runner_filter=RunnerFilter(skip_checks=['policy_id_2']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_2']), 0)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_1']), 1)

        report = cfn_runner.run(root_folder=test_files_dir,
                                runner_filter=RunnerFilter(checks=['policy_id_4']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_4']), 2)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_3']), 0)

        report = cfn_runner.run(root_folder=test_files_dir,
                                runner_filter=RunnerFilter(checks=['policy_id_3']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_3']), 1)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_4']), 0)

        report = cfn_runner.run(root_folder=test_files_dir,
                                runner_filter=RunnerFilter(skip_checks=['policy_id_3']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_3']), 0)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'policy_id_4']), 2)

    def test_pre_scan_with_cloned_checks(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True
        custom_policies_integration = CustomPoliciesIntegration(instance)

        instance.customer_run_config_response = mock_custom_policies_response()

        custom_policies_integration.pre_scan()
        cfn_registry = get_graph_checks_registry("cloudformation").checks
        tf_registry = get_graph_checks_registry("terraform").checks
        k8s_registry = get_graph_checks_registry("kubernetes").checks
        bicep_registry = get_graph_checks_registry("bicep").checks
        self.assertEqual(1, len(custom_policies_integration.bc_cloned_checks))
        self.assertEqual('kpande_AZR_1648821862291', tf_registry[0].id, cfn_registry[0].id)
        self.assertEqual('kpande_AZR_1648821862291', tf_registry[0].bc_id, cfn_registry[0].bc_id)
        self.assertEqual('kpande_kubernetes_1650378013211', k8s_registry[0].id)
        self.assertEqual('kpande_kubernetes_1650378013211', k8s_registry[0].bc_id)
        self.assertEqual('kpande_bicep_1650378013212', bicep_registry[0].id)
        self.assertEqual('kpande_bicep_1650378013212', bicep_registry[0].bc_id)

    def test_pre_scan_with_multiple_frameworks_graph_check(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True
        custom_policies_integration = CustomPoliciesIntegration(instance)

        instance.customer_run_config_response = mock_multiple_frameworks_custom_policy_response()

        custom_policies_integration.pre_scan()
        bicep_registry = get_graph_checks_registry("bicep").checks
        all_graph_checks = get_all_graph_checks_registries()
        for registry in all_graph_checks:
            multiple_frameworks_custom_policy_exist = False
            for check in registry.checks:
                if check.bc_id == 'multiple_frameworks_policy_1625063607541':
                    multiple_frameworks_custom_policy_exist = True
            self.assertEqual(True, multiple_frameworks_custom_policy_exist)
        self.assertEqual(2, len(bicep_registry))

    def test_post_runner_with_cloned_checks(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True
        custom_policies_integration = CustomPoliciesIntegration(instance)

        # mock _get_policies_from_platform method
        instance.customer_run_config_response = mock_custom_policies_response()
        custom_policies_integration.pre_scan()

        scan_reports = Report("terraform")
        record = Record(
            check_id="CKV_AWS_5",
            check_name="Ensure all data stored in the Elasticsearch is securely encrypted at rest",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path="./main.tf",
            file_line_range=[7, 10],
            resource="aws_elasticsearch_domain.enabled",
            evaluations=None,
            check_class='',
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
            bc_check_id="BC_AWS_ELASTICSEARCH_3"
        )
        scan_reports.failed_checks.append(record)

        custom_policies_integration.post_runner(scan_reports)
        self.assertEqual(2, len(scan_reports.failed_checks))
        self.assertEqual('mikepolicies_cloned_AWS_1625063607541', scan_reports.failed_checks[1].check_id)

    def test_post_runner_with_cloned_checks_with_suppression(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True
        custom_policies_integration = CustomPoliciesIntegration(instance)

        # mock _get_policies_from_platform method
        instance.customer_run_config_response = mock_custom_policies_response()
        custom_policies_integration.pre_scan()

        scan_reports = Report("terraform")
        record = Record(
            check_id="CKV_AWS_5",
            check_name="Ensure all data stored in the Elasticsearch is securely encrypted at rest",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path="./main.tf",
            file_line_range=[7, 10],
            resource="aws_elasticsearch_domain.enabled",
            evaluations=None,
            check_class='',
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
            bc_check_id="BC_AWS_ELASTICSEARCH_3"
        )

        scan_reports.failed_checks.append(record)
        custom_policies_integration.policy_level_suppression = ['BC_AWS_ELASTICSEARCH_3_80341358308']
        custom_policies_integration.post_runner(scan_reports)
        self.assertEqual(1, len(scan_reports.failed_checks))
        self.assertEqual('mikepolicies_cloned_AWS_1625063607541', scan_reports.failed_checks[0].check_id)

    def test_post_runner_with_non_failed_cloned_checks_with_suppression(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True
        custom_policies_integration = CustomPoliciesIntegration(instance)

        # mock _get_policies_from_platform method
        instance.customer_run_config_response = mock_custom_policies_response()
        failed_cloned_policy = instance.customer_run_config_response.get('customPolicies')[0]
        custom_policies_integration.pre_scan()
        custom_policies_integration.bc_cloned_checks = failed_cloned_policy

        scan_reports = Report("terraform")
        record = Record(
            check_id="CKV_AWS_5",
            check_name="Ensure all data stored in the Elasticsearch is securely encrypted at rest",
            check_result={"result": CheckResult.FAILED},
            code_block=[],
            file_path="./main.tf",
            file_line_range=[7, 10],
            resource="aws_elasticsearch_domain.enabled",
            evaluations=None,
            check_class='',
            file_abs_path=",.",
            entity_tags={"tag1": "value1"},
            bc_check_id="BC_AWS_ELASTICSEARCH_3"
        )

        scan_reports.failed_checks.append(record)
        failed_cloned_policy_record = deepcopy(record)
        failed_cloned_policy_record.check_id = failed_cloned_policy['id']
        failed_cloned_policy_record.bc_check_id = failed_cloned_policy['id']
        failed_cloned_policy_record.guideline = failed_cloned_policy['guideline']
        failed_cloned_policy_record.severity = failed_cloned_policy['severity']
        failed_cloned_policy_record.check_name = failed_cloned_policy['title']

        scan_reports.failed_checks.append(failed_cloned_policy_record)
        custom_policies_integration.policy_level_suppression = ['mikepolicies_cloned_AWS_1625063607541_80341358308']
        custom_policies_integration.post_runner(scan_reports)
        self.assertEqual(1, len(scan_reports.failed_checks))
        self.assertEqual('CKV_AWS_5', scan_reports.failed_checks[0].check_id)

    def test_policy_load_with_resources_types_as_str(self):
        # response from API
        policies = [
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
                            "operator": "equals",
                            "attribute": "xyz",
                            "cond_type": "attribute",
                            "resource_types": "aws_s3_bucket"
                        }
                    ]
                }),
                "benchmarks": {},
            },
            {
                "id": "policy_id_2",
                "title": "ui1",
                "severity": "HIGH",
                "category": "General",
                "guideline": "ui1",
                "code": json.dumps({
                    "value": "abc",
                    "operator": "equals",
                    "attribute": "region",
                    "cond_type": "attribute",
                    "resource_types": [
                        "aws_s3_bucket"
                    ]
                }),
                "benchmarks": {},
            },
            {
                "id": "policy_id_3",
                "title": "Check that all EC2 instances are tagged with yor_trace",
                "descriptiveTitle": "null",
                "constructiveTitle": "null",
                "severity": "LOW",
                "pcSeverity": "null",
                "category": "General",
                "guideline": "Check for YOR tagging",
                "code": json.dumps({
                    "operator": "exists",
                    "attribute": "Tags.yor_trace",
                    "cond_type": "attribute",
                    "resource_types": [
                        "AWS::EC2::Instance"
                    ]
                }),
                "benchmarks": {},
                "frameworks": [
                    "Terraform",
                    "CloudFormation"
                ],
            },
            {
                "id": "policy_id_4",
                "title": "Custom - ensure MSK Cluster logging is enabled",
                "descriptiveTitle": "null",
                "constructiveTitle": "null",
                "severity": "MEDIUM",
                "pcSeverity": "null",
                "category": "Logging",
                "resourceTypes": [
                    "AWS::MSK::Cluster"
                ],
                "accountsData": {},
                "guideline": "Some sample guidelines",
                "isCustom": True,
                "code": json.dumps({
                    "or": [
                        {
                            "value": "true",
                            "operator": "equals",
                            "attribute": "LoggingInfo.BrokerLogs.S3.Enabled",
                            "cond_type": "attribute",
                            "resource_types": [
                                "AWS::MSK::Cluster"
                            ]
                        },
                        {
                            "value": "true",
                            "operator": "equals",
                            "attribute": "LoggingInfo.BrokerLogs.Firehose.Enabled",
                            "cond_type": "attribute",
                            "resource_types": [
                                "AWS::MSK::Cluster"
                            ]
                        },
                        {
                            "value": "true",
                            "operator": "equals",
                            "attribute": "LoggingInfo.BrokerLogs.CloudWatchLogs.Enabled",
                            "cond_type": "attribute",
                            "resource_types": [
                                "AWS::MSK::Cluster"
                            ]
                        }
                    ]
                }),
                "benchmarks": {},
                "frameworks": [
                    "Terraform",
                    "CloudFormation"
                ],
            },
            {
                "id": "policy_id_5",
                "title": "Custom - ensure SQL pool valid create mode",
                "severity": "HIGH",
                "category": "General",
                "guideline": "Custom - ensure",
                "code": json.dumps({
                    "value": "Recovery",
                    "operator": "equals",
                    "attribute": "createMode",
                    "cond_type": "attribute",
                    "resource_types": [
                        "Microsoft.Synapse/workspaces/sqlPools"
                    ]
                }),
                "benchmarks": {},
            }
        ]

        # for this test, we simulate some of the check registry manipulation; otherwise the singleton
        # instance will be modified and break other tests.

        parser = GraphCheckParser()

        registry = Registry(parser=GraphCheckParser(), checks_dir=str(
            Path(__file__).parent.parent.parent.parent / "checkov" / "terraform" / "checks" / "graph_checks"))
        checks = [parser.parse_raw_check(CustomPoliciesIntegration._convert_raw_check(p)) for p in policies]
        registry.checks = checks  # simulate that the policy downloader will do


def mock_custom_policies_response():
    return {
        "customPolicies": [
            {
                "id": "mikepolicies_cloned_AWS_1625063607541",
                "title": "Cloned policy",
                "severity": "CRITICAL",
                "category": "General",
                "frameworks": [
                    "Terraform",
                    "CloudFormation"
                ],
                "resourceTypes": [
                    "aws_s3_bucket"
                ],
                "guideline": "mikepolicies_cloned_AWS_1625063607541",
                "benchmarks": {},
                "createdBy": "mike+policies@bridgecrew.io",
                "code": "null",
                "sourceIncidentId": "BC_AWS_ELASTICSEARCH_3"
            },
            {
                "id": "kpande_AZR_1648821862291",
                "code": "{\"and\":[{\"operator\":\"exists\",\"cond_type\":\"connection\",\"resource_types\":["
                        "\"azurerm_subnet_network_security_group_association\"],\"connected_resource_types\":["
                        "\"azurerm_subnet\",\"azurerm_network_security_group\"]},{\"value\":[\"azurerm_subnet\"],"
                        "\"operator\":\"within\",\"attribute\":\"resource_type\",\"cond_type\":\"filter\"}]}",
                "title": "Ensure subnet is associated with NSG",
                "guideline": "Every subnet should be associated with NSG for controlling access to \nresources within "
                             "the subnet.\n",
                "severity": "HIGH",
                "pcSeverity": None,
                "category": "Networking",
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "sourceIncidentId": None,
                "benchmarks": {},
                "frameworks": [
                    "CloudFormation",
                    "Terraform"
                ]
            },
            {
                "id": "kpande_kubernetes_1650378013211",
                "code": "{\"operator\":\"exists\",\"attribute\":\"spec.runAsUser.rule\",\"cond_type\":\"attribute\","
                        "\"resource_types\":[\"PodSecurityPolicy\"]}",
                "title": "k8s policy",
                "guideline": "meaningful guideline for k8s policy",
                "severity": "HIGH",
                "pcSeverity": None,
                "category": "Kubernetes",
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "sourceIncidentId": None,
                "benchmarks": {},
                "frameworks": [
                    "Kubernetes"
                ]
            },
            {
                "id": "kpande_bicep_1650378013212",
                "code": "{\"operator\":\"exists\",\"attribute\":\"spec.runAsUser.rule\",\"cond_type\":\"attribute\","
                        "\"resource_types\":[\"PodSecurityPolicy\"]}",
                "title": "bicep policy",
                "guideline": "meaningful guideline for bicep policy",
                "severity": "HIGH",
                "pcSeverity": None,
                "category": "bicep",
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "sourceIncidentId": None,
                "benchmarks": {},
                "frameworks": [
                    "bicep"
                ]
            }
        ]
    }


def mock_multiple_frameworks_custom_policy_response():
    return {
        "customPolicies": [
            {
                "id": "kpande_bicep_1650378013212",
                "code": "{\"operator\":\"exists\",\"attribute\":\"spec.runAsUser.rule\",\"cond_type\":\"attribute\","
                        "\"resource_types\":[\"PodSecurityPolicy\"]}",
                "title": "bicep policy",
                "guideline": "meaningful guideline for bicep policy",
                "severity": "HIGH",
                "pcSeverity": None,
                "category": "bicep",
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "sourceIncidentId": None,
                "benchmarks": {},
                "frameworks": [
                    "bicep"
                ]
            },
            {
                "id": "multiple_frameworks_policy_1625063607541",
                "title": "multiple frameworks policy",
                "code": "{\"and\":[{\"operator\":\"exists\",\"cond_type\":\"connection\",\"resource_types\":["
                        "\"azurerm_subnet_network_security_group_association\"],\"connected_resource_types\":["
                        "\"azurerm_subnet\",\"azurerm_network_security_group\"]},{\"value\":[\"azurerm_subnet\"],"
                        "\"operator\":\"within\",\"attribute\":\"resource_type\",\"cond_type\":\"filter\"}]}",
                "severity": "CRITICAL",
                "category": "General",
                "frameworks": [],
                "resourceTypes": ["aws_s3_bucket", "PodSecurityPolicy"],
                "guideline": "multiple_frameworks_policy_1625063607541",
                "benchmarks": {},
                "createdBy": "mike+policies@bridgecrew.io",
                "sourceIncidentId": None
            }
        ]
    }


if __name__ == '__main__':
    unittest.main()
