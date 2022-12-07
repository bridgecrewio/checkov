import os
import unittest
from typing import Any, Dict, List

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.secrets.plugins.custom_regex_detector import modify_secrets_policy_to_detectors, CustomRegexDetector
from checkov.secrets.runner import Runner


class TestCustomRegexDetector(unittest.TestCase):

    def test_modify_secrets_policy_to_detectors(self) -> None:
        policies_list: List[Dict[str, Any]] = [
            {
                "incidentId": "test1",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test",
                "guideline": "test",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes": [
                    "aws_instance"
                ],
                "provider": "AWS",
                "remediationIds": [],
                "conditionQuery": {
                    "or": [
                        {
                            "value": "t3.micro",
                            "operator": "equals",
                            "attribute": "instance_type",
                            "cond_type": "attribute",
                            "resource_types": [
                                "aws_instance"
                            ]
                        },
                        {
                            "value": "t3.nano",
                            "operator": "equals",
                            "attribute": "instance_type",
                            "cond_type": "attribute",
                            "resource_types": [
                                "aws_instance"
                            ]
                        }
                    ]
                },
                "customerName": "lshind",
                "isCustom": True,
                "code": "---\nmetadata:\n  name: \"test\" #give your custom policy a unique name \n  guidelines: \"test\" #add text that explains the configuration the policy looks for, its implications, and how to fix it\n  category: \"secrets\" #choose one: \"general\"/\"elasticsearch\"/\"iam\"/\"kubernetes\"/\"logging\"/\"monitoring\"/\"networking\"/\"public\"/\"secrets\"/\"serverless\"/\"storage\"\n  severity: \"medium\" #choose one: \"critical\"/\"high\"/\"medium\"/\"low\"\nscope:\n  provider: \"aws\" #choose one: \"aws\"/\"azure\"/\"gcp\"/\"kubernetes\"\ndefinition: #define the conditions the policy searches for.\n# The example below checks EC2s with instance_type t3.micro or t3.nano. for more examples please visit our docs - https://docs.bridgecrew.io/docs/yaml-format-for-custom-policies\n or:\n  - cond_type: \"attribute\"\n    resource_types:\n    - \"aws_instance\"\n    attribute: \"instance_type\"\n    operator: \"equals\"\n    value: \"t3.micro\"\n  - cond_type: \"attribute\"\n    resource_types:\n    - \"aws_instance\"\n    attribute: \"instance_type\"\n    operator: \"equals\"\n    value: \"t3.nano\"\n",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "frameworks": [
                    "CloudFormation",
                    "Terraform"
                ],
                "pcSeverity": None,
                "sourceIncidentId": None
            },
            {
                "incidentId": "test1",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test",
                "guideline": "test",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test1",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - abcdefg",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            },
            {
                "incidentId": "test2",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test",
                "guideline": "test2",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - 1234567",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]
        detector_obj = modify_secrets_policy_to_detectors(policies_list)
        detectors_result: List[Dict[str, Any]] = [{
            "Name": "test1",
            "Check_ID": "test1",
            "Regex": "abcdefg"
        },
            {
                "Name": "test2",
                "Check_ID": "test2",
                "Regex": "1234567"
            }]
        detector_obj.sort(key=lambda detector: detector['Check_ID'])
        detectors_result.sort(key=lambda detector: detector['Check_ID'])  # type: ignore
        assert all(
            True for x in range(0, len(detector_obj)) if detector_obj[x]['Check_ID'] == detectors_result[x]['Check_ID'])
        assert len(detectors_result) == len(detector_obj)


    def test_test_custom_regex_detector(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/custom_regex_detector"
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": "test1",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test1",
                "guideline": "test",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test1",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?:^|\W)HANA(?:$|\W)",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            },
            {
                "incidentId": "test2",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test2",
                "guideline": "test2",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?:^|\W)LIR(?:$|\W)",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path,
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 3)

    def test_test_custom_regex_detector_in_custom_limit_characters(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/custom_regex_detector"
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": "test2",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test2",
                "guideline": "test2",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:test)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path,
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 1)

    def test_test_custom_regex_detector_out_custom_limit_characters(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/custom_regex_detector"
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": "test2",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test2",
                "guideline": "test2",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:out)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path,
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 0)