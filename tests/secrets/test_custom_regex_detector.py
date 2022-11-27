import unittest
from typing import Any, Dict, List

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.secrets.plugins.custom_regex_detector import modify_secrets_policy_to_detectors, CustomRegexDetector


class TestCustomRegexDetector(unittest.TestCase):

    def test_modify_secrets_policy_to_detectors(self) -> None:
        policies_list: List[Dict[str, Any]] = [
            {
                "incidentId": "lshindelman1_AWS_1666860510378",
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
                "customerName": "lshindelman1",
                "isCustom": True,
                "createdBy": "lshindelman+1@paloaltonetworks.com",
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
            }
        ]
        detector_obj = modify_secrets_policy_to_detectors(policies_list)
        detectors_result: List[Dict[str, Any]] = []
        detector_obj.sort(key=lambda detector: detector['Check_ID'])
        detectors_result.sort(key=lambda detector: detector['Check_ID'])  # type: ignore
        assert all(
            True for x in range(0, len(detector_obj)) if detector_obj[x]['Check_ID'] == detectors_result[x]['Check_ID'])
        assert len(detectors_result) == len(detector_obj)

    def test_test_custom_regex_detector(self) -> None:
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": "lshindelman1_AWS_1666860510378",
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
                "conditionQuery":
                    {
                        "or":
                            [
                                {
                                    "value": "t3.micro",
                                    "operator": "equals",
                                    "attribute": "instance_type",
                                    "cond_type": "attribute",
                                    "resource_types":
                                        [
                                            "aws_instance"
                                        ]
                                },
                                {
                                    "value": "t3.nano",
                                    "operator": "equals",
                                    "attribute": "instance_type",
                                    "cond_type": "attribute",
                                    "resource_types":
                                        [
                                            "aws_instance"
                                        ]
                                }
                            ]
                    },
                "customerName": "lshindelman1",
                "isCustom": True,
                "createdBy": "lshindelman+1@paloaltonetworks.com",
                "code": "---\nmetadata:\n  name: \"test\" #give your custom policy a unique name \n  guidelines: \"test\" #add text that explains the configuration the policy looks for, its implications, and how to fix it\n  category: \"secrets\" #choose one: \"general\"/\"elasticsearch\"/\"iam\"/\"kubernetes\"/\"logging\"/\"monitoring\"/\"networking\"/\"public\"/\"secrets\"/\"serverless\"/\"storage\"\n  severity: \"medium\" #choose one: \"critical\"/\"high\"/\"medium\"/\"low\"\nscope:\n  provider: \"aws\" #choose one: \"aws\"/\"azure\"/\"gcp\"/\"kubernetes\"\ndefinition: #define the conditions the policy searches for.\n# The example below checks EC2s with instance_type t3.micro or t3.nano. for more examples please visit our docs - https://docs.bridgecrew.io/docs/yaml-format-for-custom-policies\n or:\n  - cond_type: \"attribute\"\n    resource_types:\n    - \"aws_instance\"\n    attribute: \"instance_type\"\n    operator: \"equals\"\n    value: \"t3.micro\"\n  - cond_type: \"attribute\"\n    resource_types:\n    - \"aws_instance\"\n    attribute: \"instance_type\"\n    operator: \"equals\"\n    value: \"t3.nano\"\n",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "frameworks":
                    [
                        "CloudFormation",
                        "Terraform"
                    ],
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}

        detector_obj = CustomRegexDetector()

        assert len(detector_obj.denylist) == 0
        assert len(detector_obj.regex_to_metadata) == 0
