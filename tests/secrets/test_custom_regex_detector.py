import os
import unittest
from typing import Any, Dict, List

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner
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
            },
            {
                "incidentId": "BC_GIT_33",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Databricks Authentication Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_33",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_33",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(dsapi[a-h0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Databricks Authentication Token",
                "constructiveTitle": "Databricks Authentication Token",
                "pcPolicyId": "1979aa5f-0e33-4521-b7aa-0d7f18f298ca",
                "additionalPcPolicyIds": [
                    "1979aa5f-0e33-4521-b7aa-0d7f18f298ca"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_34",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "DigitalOcean Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_34",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_34",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:digitalocean)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{64})\\b",
                "descriptiveTitle": "DigitalOcean Token",
                "constructiveTitle": "DigitalOcean Token",
                "pcPolicyId": "0a2d7460-9379-438d-9e0b-ab2976a826e0",
                "additionalPcPolicyIds": [
                    "0a2d7460-9379-438d-9e0b-ab2976a826e0"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_35",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Discord Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_35",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_35",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{18})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Discord Token",
                "constructiveTitle": "Discord Token",
                "pcPolicyId": "b0e5f091-e7de-4d70-bbcf-3289a307c0eb",
                "additionalPcPolicyIds": [
                    "b0e5f091-e7de-4d70-bbcf-3289a307c0eb"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_37",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "DroneCI Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_37",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_37",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:droneci)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "DroneCI Token",
                "constructiveTitle": "DroneCI Token",
                "pcPolicyId": "5686a696-223c-4b07-b5bf-427c780125a9",
                "additionalPcPolicyIds": [
                    "5686a696-223c-4b07-b5bf-427c780125a9"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_40",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Elastic Email Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_40",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_40",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:elastic)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{96})\\b",
                "descriptiveTitle": "Elastic Email Key",
                "constructiveTitle": "Elastic Email Key",
                "pcPolicyId": "9567784e-cd7a-4fdf-9dc1-dcf90adbe6b1",
                "additionalPcPolicyIds": [
                    "9567784e-cd7a-4fdf-9dc1-dcf90adbe6b1"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_41",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Fastly Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_41",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_41",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:fastly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Fastly Personal Token",
                "constructiveTitle": "Fastly Personal Token",
                "pcPolicyId": "96ca6d09-8c3e-47f2-b5d7-f5c2181fb387",
                "additionalPcPolicyIds": [
                    "96ca6d09-8c3e-47f2-b5d7-f5c2181fb387"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_42",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "FullStory API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_42",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_42",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:fullstory)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9/+]{88})\\b",
                "descriptiveTitle": "FullStory API Key",
                "constructiveTitle": "FullStory API Key",
                "pcPolicyId": "84c57881-ad48-4959-8036-84c20699c43d",
                "additionalPcPolicyIds": [
                    "84c57881-ad48-4959-8036-84c20699c43d"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_43",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "GitHub Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_43",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_43",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - gh[pousr]_[0-9a-zA-Z]{36}",
                "descriptiveTitle": "GitHub Token",
                "constructiveTitle": "GitHub Token",
                "pcPolicyId": "7864b6ac-5de9-4845-81f0-b9d9de32a0ca",
                "additionalPcPolicyIds": [
                    "7864b6ac-5de9-4845-81f0-b9d9de32a0ca"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_44",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "GitLab Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_44",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_44",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - glpat-[0-9a-zA-Z\\-\\_]{20}",
                "descriptiveTitle": "GitLab Token",
                "constructiveTitle": "GitLab Token",
                "pcPolicyId": "14db94b2-590d-484b-98c5-b96aec2cfe97",
                "additionalPcPolicyIds": [
                    "14db94b2-590d-484b-98c5-b96aec2cfe97"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_45",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Google Cloud Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_45",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_45",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(AIza[0-9A-Za-z\\\\-_]{35})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Google Cloud Keys",
                "constructiveTitle": "Google Cloud Keys",
                "pcPolicyId": "9d1b426e-4498-4660-a34f-8a43beb0a2b7",
                "additionalPcPolicyIds": [
                    "9d1b426e-4498-4660-a34f-8a43beb0a2b7"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_46",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Grafana Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_46",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_46",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(eyJrIjoi[A-Za-z0-9]{70,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(glc_[A-Za-z0-9+/]{32,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(glsa_[A-Za-z0-9]{32}_[A-Fa-f0-9]{8})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Grafana Token",
                "constructiveTitle": "Grafana Token",
                "pcPolicyId": "b0a8cae4-c04e-4a99-a64e-b582d3e83000",
                "additionalPcPolicyIds": [
                    "b0a8cae4-c04e-4a99-a64e-b582d3e83000"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_47",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Terraform Cloud API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_47",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_47",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}\n  - (?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}",
                "descriptiveTitle": "Terraform Cloud API Token",
                "constructiveTitle": "Terraform Cloud API Token",
                "pcPolicyId": "56b81a7c-1927-405e-be9e-c3213af08142",
                "additionalPcPolicyIds": [
                    "56b81a7c-1927-405e-be9e-c3213af08142"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_48",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Heroku Platform Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_48",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_48",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:heroku)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Heroku Platform Key",
                "constructiveTitle": "Heroku Platform Key",
                "pcPolicyId": "ab6c1821-7b25-43d6-9ff0-ba300479c1ac",
                "additionalPcPolicyIds": [
                    "ab6c1821-7b25-43d6-9ff0-ba300479c1ac"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_49",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "HubSpot API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_49",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_49",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:hubspot)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "HubSpot API Key",
                "constructiveTitle": "HubSpot API Key",
                "pcPolicyId": "bfdda3a2-e2d2-4bfb-ba7d-49466c108a88",
                "additionalPcPolicyIds": [
                    "bfdda3a2-e2d2-4bfb-ba7d-49466c108a88"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_50",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Intercom Access Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_50",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_50",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:intercom)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{60})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Intercom Access Token",
                "constructiveTitle": "Intercom Access Token",
                "pcPolicyId": "1abf6697-5737-4067-8cbc-c060ca8cf331",
                "additionalPcPolicyIds": [
                    "1abf6697-5737-4067-8cbc-c060ca8cf331"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_51",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Jira Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_51",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_51",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9]{24})\\b\n  - (?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([\\w\\-\\.]+@(?:[\\w-]+\\.)+[\\w-]{2,4})\\b",
                "descriptiveTitle": "Jira Token",
                "constructiveTitle": "Jira Token",
                "pcPolicyId": "afa159db-75a7-451c-9731-9a353c6e6a78",
                "additionalPcPolicyIds": [
                    "afa159db-75a7-451c-9731-9a353c6e6a78"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_52",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "LaunchDarkly Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_52",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_52",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:launchdarkly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "LaunchDarkly Personal Token",
                "constructiveTitle": "LaunchDarkly Personal Token",
                "pcPolicyId": "90828b95-50f6-42ed-bc3f-4cc8a80e0250",
                "additionalPcPolicyIds": [
                    "90828b95-50f6-42ed-bc3f-4cc8a80e0250"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_53",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Netlify Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_53",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_53",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:netlify)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40,46})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Netlify Token",
                "constructiveTitle": "Netlify Token",
                "pcPolicyId": "516fde21-67e9-4573-bfe7-41f6c5b8f5c0",
                "additionalPcPolicyIds": [
                    "516fde21-67e9-4573-bfe7-41f6c5b8f5c0"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_54",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "New Relic Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_54",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_54",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRAK-[a-z0-9]{27})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRJS-[a-f0-9]{19})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "New Relic Key",
                "constructiveTitle": "New Relic Key",
                "pcPolicyId": "b2b74119-7057-4412-8b7d-fdf40e3cc916",
                "additionalPcPolicyIds": [
                    "b2b74119-7057-4412-8b7d-fdf40e3cc916"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_55",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Notion Integration Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_55",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_55",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - \\b(secret_[A-Za-z0-9]{43})\\b",
                "descriptiveTitle": "Notion Integration Token",
                "constructiveTitle": "Notion Integration Token",
                "pcPolicyId": "8dcf5a77-4822-49f5-ab61-fcd7c748feea",
                "additionalPcPolicyIds": [
                    "8dcf5a77-4822-49f5-ab61-fcd7c748feea"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_56",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Okta Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_56",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_56",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:okta)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{42})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Okta Token",
                "constructiveTitle": "Okta Token",
                "pcPolicyId": "ded6eeb0-ff9e-4455-bb8b-b9a5754fb758",
                "additionalPcPolicyIds": [
                    "ded6eeb0-ff9e-4455-bb8b-b9a5754fb758"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_57",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "PagerDuty Authorization Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_57",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_57",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:pagerduty)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z]{1}\\+[a-zA-Z]{9}\\-[a-z]{2}\\-[a-z0-9]{5})\\b",
                "descriptiveTitle": "PagerDuty Authorization Token",
                "constructiveTitle": "PagerDuty Authorization Token",
                "pcPolicyId": "e66683fb-cce5-4b61-8a20-03fadc90d390",
                "additionalPcPolicyIds": [
                    "e66683fb-cce5-4b61-8a20-03fadc90d390"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_58",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "PlanetScale Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_58",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_58",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(pscale_pw_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(pscale_tkn_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(pscale_oauth_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "PlanetScale Token",
                "constructiveTitle": "PlanetScale Token",
                "pcPolicyId": "d671864e-5c7b-423b-bfe2-2ede45e8d18a",
                "additionalPcPolicyIds": [
                    "d671864e-5c7b-423b-bfe2-2ede45e8d18a"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_59",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Postman API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_59",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_59",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(PMAK-(?i)[a-f0-9]{24}\\-[a-f0-9]{34})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Postman API Key",
                "constructiveTitle": "Postman API Key",
                "pcPolicyId": "a183a84f-e1f0-4751-bdaa-b3b799ec3dd4",
                "additionalPcPolicyIds": [
                    "a183a84f-e1f0-4751-bdaa-b3b799ec3dd4"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_60",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Pulumi Access Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_60",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_60",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(pul-[a-f0-9]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Pulumi Access Token",
                "constructiveTitle": "Pulumi Access Token",
                "pcPolicyId": "b2ec65ce-9bc0-463e-b8e2-92d38423183a",
                "additionalPcPolicyIds": [
                    "b2ec65ce-9bc0-463e-b8e2-92d38423183a"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_61",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Python Package Index Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_61",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_61",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\\-_]{50,1000}",
                "descriptiveTitle": "Python Package Index Key",
                "constructiveTitle": "Python Package Index Key",
                "pcPolicyId": "ce61d4a3-bc17-494a-86f1-40d26fa73b1f",
                "additionalPcPolicyIds": [
                    "ce61d4a3-bc17-494a-86f1-40d26fa73b1f"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_62",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "RapidAPI Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_62",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_62",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:rapidapi)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{50})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "RapidAPI Key",
                "constructiveTitle": "RapidAPI Key",
                "pcPolicyId": "1f01777e-9839-47c3-bd90-e840a464b17b",
                "additionalPcPolicyIds": [
                    "1f01777e-9839-47c3-bd90-e840a464b17b"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_63",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Readme API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_63",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_63",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(rdme_[a-z0-9]{70})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Readme API Key",
                "constructiveTitle": "Readme API Key",
                "pcPolicyId": "be223514-2ba7-4937-80d8-2bc725d201c1",
                "additionalPcPolicyIds": [
                    "be223514-2ba7-4937-80d8-2bc725d201c1"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_64",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "RubyGems API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_64",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_64",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(rubygems_[a-f0-9]{48})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "RubyGems API Key",
                "constructiveTitle": "RubyGems API Key",
                "pcPolicyId": "2a6b9d00-c551-4f66-865a-9e9950886745",
                "additionalPcPolicyIds": [
                    "2a6b9d00-c551-4f66-865a-9e9950886745"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_65",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Sentry Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_65",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_65",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:sentry)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Sentry Token",
                "constructiveTitle": "Sentry Token",
                "pcPolicyId": "77cc76d6-34e9-4aea-8168-508e8c9b35bb",
                "additionalPcPolicyIds": [
                    "77cc76d6-34e9-4aea-8168-508e8c9b35bb"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_66",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Splunk User Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_66",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_66",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:splunk)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9A-Z]{22})\\b",
                "descriptiveTitle": "Splunk User Credentials",
                "constructiveTitle": "Splunk User Credentials",
                "pcPolicyId": "6933e817-4991-4f9d-9bbf-b11bacfc8c29",
                "additionalPcPolicyIds": [
                    "6933e817-4991-4f9d-9bbf-b11bacfc8c29"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_67",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Sumo Logic Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_67",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_67",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{14})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Sumo Logic Keys",
                "constructiveTitle": "Sumo Logic Keys",
                "pcPolicyId": "b5ba4ba2-8e01-4055-8086-e97a5ef5b598",
                "additionalPcPolicyIds": [
                    "b5ba4ba2-8e01-4055-8086-e97a5ef5b598"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_68",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Telegram Bot Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_68",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_68",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:telegram)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9]{8,10}:[a-zA-Z0-9_-]{35})\\b",
                "descriptiveTitle": "Telegram Bot Token",
                "constructiveTitle": "Telegram Bot Token",
                "pcPolicyId": "bbe5b7b7-00e1-4c4f-8838-02d913a3df11",
                "additionalPcPolicyIds": [
                    "bbe5b7b7-00e1-4c4f-8838-02d913a3df11"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_69",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Travis Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_69",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_69",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:travis)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{22})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Travis Personal Token",
                "constructiveTitle": "Travis Personal Token",
                "pcPolicyId": "9337a600-63d8-4b20-8492-6f6900ed2b6f",
                "additionalPcPolicyIds": [
                    "9337a600-63d8-4b20-8492-6f6900ed2b6f"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_70",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Typeform API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_70",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_70",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:typeform)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(tfp_[a-z0-9\\-_\\.=]{59})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Typeform API Token",
                "constructiveTitle": "Typeform API Token",
                "pcPolicyId": "4d0f2321-6866-4fa9-b57c-1d7db2801acb",
                "additionalPcPolicyIds": [
                    "4d0f2321-6866-4fa9-b57c-1d7db2801acb"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_71",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Vault Unseal Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_71",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_71",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(hvs\\.[a-z0-9_-]{90,100})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(hvb\\.[a-z0-9_-]{138,212})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Vault Unseal Key",
                "constructiveTitle": "Vault Unseal Key",
                "pcPolicyId": "d29f067e-31c9-44a2-b4e0-90a25b8595e1",
                "additionalPcPolicyIds": [
                    "d29f067e-31c9-44a2-b4e0-90a25b8595e1"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_72",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Yandex Predictor API key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_72",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_72",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(YC[a-zA-Z0-9_\\-]{38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(AQVN[A-Za-z0-9_\\-]{35,38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(t1\\.[A-Z0-9a-z_-]+[=]{0,2}\\.[A-Z0-9a-z_-]{86}[=]{0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Yandex Predictor API key",
                "constructiveTitle": "Yandex Predictor API key",
                "pcPolicyId": "063f37de-6e7e-4d1f-8607-36502f9dfeaa",
                "additionalPcPolicyIds": [
                    "063f37de-6e7e-4d1f-8607-36502f9dfeaa"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_74",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Vercel API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_74",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_74",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:vercel)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9]{24})\\b",
                "descriptiveTitle": "Vercel API Token",
                "constructiveTitle": "Vercel API Token",
                "pcPolicyId": "0e6cee83-8605-44a0-b53e-8410872d0cea",
                "additionalPcPolicyIds": [
                    "0e6cee83-8605-44a0-b53e-8410872d0cea"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_75",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Webflow API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_75",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_75",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:webflow)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA0-9]{64})\\b",
                "descriptiveTitle": "Webflow API Token",
                "constructiveTitle": "Webflow API Token",
                "pcPolicyId": "7fc2545b-e320-4d5c-900c-d9218fe286c3",
                "additionalPcPolicyIds": [
                    "7fc2545b-e320-4d5c-900c-d9218fe286c3"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_76",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Scalr API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_76",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_76",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:scalr)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9a-zA-Z.\\-_]{136})\n  - (?i)(?:scalr)(?:.|[\\n\\r]){0,40}\\b(at\\-(?:[0-9a-z]{12,20}))\\b",
                "descriptiveTitle": "Scalr API Token",
                "constructiveTitle": "Scalr API Token",
                "pcPolicyId": "6e65aa0b-c144-476e-90c4-1a8d1cd9e725",
                "additionalPcPolicyIds": [
                    "6e65aa0b-c144-476e-90c4-1a8d1cd9e725"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_73",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Cloudflare API Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_73",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_73",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:cloudflare)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{40})\\b",
                "descriptiveTitle": "Cloudflare API Credentials",
                "constructiveTitle": "Cloudflare API Credentials",
                "pcPolicyId": "fbf7538b-dd40-4afe-a27d-81e118980598",
                "additionalPcPolicyIds": [
                    "fbf7538b-dd40-4afe-a27d-81e118980598"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_36",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Doppler API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_36",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_36",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (dp\\.pt\\.)(?i)[a-z0-9]{43}",
                "descriptiveTitle": "Doppler API Key",
                "constructiveTitle": "Doppler API Key",
                "pcPolicyId": "009c3b4c-16cf-4c85-9b1d-4ab39fdbfb8b",
                "additionalPcPolicyIds": [
                    "009c3b4c-16cf-4c85-9b1d-4ab39fdbfb8b"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_21",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Airtable API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_21",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_21",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:airtable)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{17})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Airtable API Key",
                "constructiveTitle": "Airtable API Key",
                "pcPolicyId": "8058279d-25be-4115-bd84-6b830faa3c5d",
                "additionalPcPolicyIds": [
                    "8058279d-25be-4115-bd84-6b830faa3c5d"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_22",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Algolia Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_22",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_22",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:algolia)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Algolia Key",
                "constructiveTitle": "Algolia Key",
                "pcPolicyId": "1ea47a16-0199-4117-93f9-01de3fcdd814",
                "additionalPcPolicyIds": [
                    "1ea47a16-0199-4117-93f9-01de3fcdd814"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_23",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Alibaba Cloud Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_23",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_23",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:alibaba)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{30})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Alibaba Cloud Keys",
                "constructiveTitle": "Alibaba Cloud Keys",
                "pcPolicyId": "34a51c97-a8be-444b-816b-06ff2c99b462",
                "additionalPcPolicyIds": [
                    "34a51c97-a8be-444b-816b-06ff2c99b462"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_24",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Asana Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_24",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_24",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Asana Key",
                "constructiveTitle": "Asana Key",
                "pcPolicyId": "250a1587-69ae-4878-8a7c-6c300eb9132f",
                "additionalPcPolicyIds": [
                    "250a1587-69ae-4878-8a7c-6c300eb9132f"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_25",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Atlassian Oauth2 Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_25",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_25",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:atlassian|confluence|jira)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Atlassian Oauth2 Keys",
                "constructiveTitle": "Atlassian Oauth2 Keys",
                "pcPolicyId": "550b4cdd-b107-4bd7-8397-a38b8e32f713",
                "additionalPcPolicyIds": [
                    "550b4cdd-b107-4bd7-8397-a38b8e32f713"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_26",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Auth0 Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_26",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_26",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:auth0)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9_-]{32,60})\\b",
                "descriptiveTitle": "Auth0 Keys",
                "constructiveTitle": "Auth0 Keys",
                "pcPolicyId": "8ebec33d-9b5e-4a9d-8796-0da742b67bef",
                "additionalPcPolicyIds": [
                    "8ebec33d-9b5e-4a9d-8796-0da742b67bef"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_27",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Bitbucket Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_27",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_27",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Bitbucket Keys",
                "constructiveTitle": "Bitbucket Keys",
                "pcPolicyId": "afcada96-ce49-4e3a-b05a-c72da1b68083",
                "additionalPcPolicyIds": [
                    "afcada96-ce49-4e3a-b05a-c72da1b68083"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_28",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Buildkite Agent Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_28",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_28",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:buildkite)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9]{40})\\b",
                "descriptiveTitle": "Buildkite Agent Token",
                "constructiveTitle": "Buildkite Agent Token",
                "pcPolicyId": "b440bbd1-34e4-48dd-ae3d-89738d508ff3",
                "additionalPcPolicyIds": [
                    "b440bbd1-34e4-48dd-ae3d-89738d508ff3"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_29",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "CircleCI Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_29",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_29",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:circle)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-fA-F0-9]{40})",
                "descriptiveTitle": "CircleCI Personal Token",
                "constructiveTitle": "CircleCI Personal Token",
                "pcPolicyId": "10fac584-5171-4acb-8fcf-818c48e93cd5",
                "additionalPcPolicyIds": [
                    "10fac584-5171-4acb-8fcf-818c48e93cd5"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_30",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Codecov API key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_30",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_30",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:codecov)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Codecov API key",
                "constructiveTitle": "Codecov API key",
                "pcPolicyId": "d047a76c-6d7f-4281-bcb9-9e9c79b896d2",
                "additionalPcPolicyIds": [
                    "d047a76c-6d7f-4281-bcb9-9e9c79b896d2"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_31",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Coinbase Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_31",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_31",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:coinbase)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Coinbase Keys",
                "constructiveTitle": "Coinbase Keys",
                "pcPolicyId": "d54bf289-817a-41bc-8f31-3502ab3db364",
                "additionalPcPolicyIds": [
                    "d54bf289-817a-41bc-8f31-3502ab3db364"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_32",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Confluent Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_32",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_32",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Confluent Keys",
                "constructiveTitle": "Confluent Keys",
                "pcPolicyId": "720b664c-19cb-4e26-a6e5-1beb402734a5",
                "additionalPcPolicyIds": [
                    "720b664c-19cb-4e26-a6e5-1beb402734a5"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_38",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Dropbox App Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_38",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_38",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{15})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(sl\\.[a-z0-9\\-=_]{135})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Dropbox App Credentials",
                "constructiveTitle": "Dropbox App Credentials",
                "pcPolicyId": "8f4d0292-8ddc-4505-a52d-3ce1280fc321",
                "additionalPcPolicyIds": [
                    "8f4d0292-8ddc-4505-a52d-3ce1280fc321"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_39",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Dynatrace token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_39",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_39",
                "resourceTypes": [
                    "*"
                ],
                "provider": "Git",
                "remediationIds": [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Dynatrace token",
                "constructiveTitle": "Dynatrace token",
                "pcPolicyId": "a4e5aa1e-94ba-4aa1-ab46-1f137b10110c",
                "additionalPcPolicyIds": [
                    "a4e5aa1e-94ba-4aa1-ab46-1f137b10110c"
                ],
                "frameworks": [
                    "Git"
                ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            }
        ]
        detector_obj = modify_secrets_policy_to_detectors(policies_list)
        detectors_result: List[Dict[str, Any]] = [
            {
                "Name": "Github Token",
                "Check_ID": "CKV_SECRET_43",
                "Regex": "gh[pousr]_[0-9a-zA-Z]{36}"
            },
            {
                "Name": "Gitlab Token",
                "Check_ID": "CKV_SECRET_44",
                "Regex": "glpat-[0-9a-zA-Z\\-\\_]{20}"
            },
            {
                "Name": "Asana Key",
                "Check_ID": "CKV_SECRET_24",
                "Regex": "(?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Asana Key",
                "Check_ID": "CKV_SECRET_24",
                "Regex": "(?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Grafana Token",
                "Check_ID": "CKV_SECRET_46",
                "Regex": "(?i)\\b(eyJrIjoi[A-Za-z0-9]{70,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Grafana Token",
                "Check_ID": "CKV_SECRET_46",
                "Regex": "(?i)\\b(glc_[A-Za-z0-9+/]{32,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Grafana Token",
                "Check_ID": "CKV_SECRET_46",
                "Regex": "(?i)\\b(glsa_[A-Za-z0-9]{32}_[A-Fa-f0-9]{8})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Terraform Cloud API Token",
                "Check_ID": "CKV_SECRET_47",
                "Regex": "(?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}"
            },
            {
                "Name": "Alibaba Cloud Key",
                "Check_ID": "CKV_SECRET_23",
                "Regex": "(?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Alibaba Cloud Key",
                "Check_ID": "CKV_SECRET_23",
                "Regex": "(?i)(?:alibaba)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{30})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Alibaba Cloud Key",
                "Check_ID": "CKV_SECRET_23",
                "Regex": "(?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Atlassian Oauth2 Key",
                "Check_ID": "CKV_SECRET_25",
                "Regex": "(?i)(?:atlassian|confluence|jira)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Algolia Key",
                "Check_ID": "CKV_SECRET_22",
                "Regex": "(?i)(?:algolia)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Airtable API Key",
                "Check_ID": "CKV_SECRET_21",
                "Regex": "(?i)(?:airtable)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{17})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Bitbucket Key",
                "Check_ID": "CKV_SECRET_27",
                "Regex": "(?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Bitbucket Key",
                "Check_ID": "CKV_SECRET_27",
                "Regex": "(?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Codecov API Key",
                "Check_ID": "CKV_SECRET_30",
                "Regex": "(?i)(?:codecov)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Coinbase Key",
                "Check_ID": "CKV_SECRET_31",
                "Regex": "(?i)(?:coinbase)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Confluent Key",
                "Check_ID": "CKV_SECRET_32",
                "Regex": "(?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Confluent Key",
                "Check_ID": "CKV_SECRET_32",
                "Regex": "(?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Databricks Token",
                "Check_ID": "CKV_SECRET_33",
                "Regex": "(?i)\\b(dsapi[a-h0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Discord Token",
                "Check_ID": "CKV_SECRET_35",
                "Regex": "(?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Discord Token",
                "Check_ID": "CKV_SECRET_35",
                "Regex": "(?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{18})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Discord Token",
                "Check_ID": "CKV_SECRET_35",
                "Regex": "(?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Doppler API Key",
                "Check_ID": "CKV_SECRET_36",
                "Regex": "(dp\\.pt\\.)(?i)[a-z0-9]{43}"
            },
            {
                "Name": "DroneCI Token",
                "Check_ID": "CKV_SECRET_37",
                "Regex": "(?i)(?:droneci)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Dropbox App Key",
                "Check_ID": "CKV_SECRET_38",
                "Regex": "(?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{15})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Dropbox App Key",
                "Check_ID": "CKV_SECRET_38",
                "Regex": "(?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(sl\\.[a-z0-9\\-=_]{135})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Dropbox App Key",
                "Check_ID": "CKV_SECRET_38",
                "Regex": "(?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Dynatrace Token",
                "Check_ID": "CKV_SECRET_39",
                "Regex": "(?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Fastly API Token",
                "Check_ID": "CKV_SECRET_41",
                "Regex": "(?i)(?:fastly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Google Cloud Key",
                "Check_ID": "CKV_SECRET_45",
                "Regex": "(?i)\\b(AIza[0-9A-Za-z\\\\-_]{35})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Terraform Cloud API Token",
                "Check_ID": "CKV_SECRET_47",
                "Regex": "(?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}"
            },
            {
                "Name": "Heroku Platform Key",
                "Check_ID": "CKV_SECRET_48",
                "Regex": "(?i)(?:heroku)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "HubSpot API Key",
                "Check_ID": "CKV_SECRET_49",
                "Regex": "(?i)(?:hubspot)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Intercom API Token",
                "Check_ID": "CKV_SECRET_50",
                "Regex": "(?i)(?:intercom)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{60})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "LaunchDarkly Token",
                "Check_ID": "CKV_SECRET_52",
                "Regex": "(?i)(?:launchdarkly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Netlify Token",
                "Check_ID": "CKV_SECRET_53",
                "Regex": "(?i)(?:netlify)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40,46})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "New Relic Key",
                "Check_ID": "CKV_SECRET_54",
                "Regex": "(?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRAK-[a-z0-9]{27})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "New Relic Key",
                "Check_ID": "CKV_SECRET_54",
                "Regex": "(?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "New Relic Key",
                "Check_ID": "CKV_SECRET_54",
                "Regex": "(?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRJS-[a-f0-9]{19})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Okta Token",
                "Check_ID": "CKV_SECRET_56",
                "Regex": "(?i)(?:okta)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{42})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "PlanetScale Token",
                "Check_ID": "CKV_SECRET_58",
                "Regex": "(?i)\\b(pscale_pw_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "PlanetScale Token",
                "Check_ID": "CKV_SECRET_58",
                "Regex": "(?i)\\b(pscale_tkn_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "PlanetScale Token",
                "Check_ID": "CKV_SECRET_58",
                "Regex": "(?i)\\b(pscale_oauth_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Postman API Key",
                "Check_ID": "CKV_SECRET_59",
                "Regex": "(?i)\\b(PMAK-(?i)[a-f0-9]{24}\\-[a-f0-9]{34})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Pulumi Token",
                "Check_ID": "CKV_SECRET_60",
                "Regex": "(?i)\\b(pul-[a-f0-9]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Python Package Index Key",
                "Check_ID": "CKV_SECRET_61",
                "Regex": "pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\\-_]{50,1000}"
            },
            {
                "Name": "RapidAPI Key",
                "Check_ID": "CKV_SECRET_62",
                "Regex": "(?i)(?:rapidapi)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{50})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Readme API Key",
                "Check_ID": "CKV_SECRET_63",
                "Regex": "(?i)\\b(rdme_[a-z0-9]{70})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "RubyGems API Key",
                "Check_ID": "CKV_SECRET_64",
                "Regex": "(?i)\\b(rubygems_[a-f0-9]{48})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Sentry Token",
                "Check_ID": "CKV_SECRET_65",
                "Regex": "(?i)(?:sentry)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Sumo Logic Key",
                "Check_ID": "CKV_SECRET_67",
                "Regex": "(?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{14})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Sumo Logic Key",
                "Check_ID": "CKV_SECRET_67",
                "Regex": "(?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Travis Token",
                "Check_ID": "CKV_SECRET_69",
                "Regex": "(?i)(?:travis)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{22})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Typeform API Token",
                "Check_ID": "CKV_SECRET_70",
                "Regex": "(?i)(?:typeform)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(tfp_[a-z0-9\\-_\\.=]{59})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Vault Unseal Key",
                "Check_ID": "CKV_SECRET_71",
                "Regex": "(?i)\\b(hvs\\.[a-z0-9_-]{90,100})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Vault Unseal Key",
                "Check_ID": "CKV_SECRET_71",
                "Regex": "(?i)\\b(hvb\\.[a-z0-9_-]{138,212})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Yandex Predictor API key",
                "Check_ID": "CKV_SECRET_72",
                "Regex": "(?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(YC[a-zA-Z0-9_\\-]{38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Yandex Predictor API key",
                "Check_ID": "CKV_SECRET_72",
                "Regex": "(?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(AQVN[A-Za-z0-9_\\-]{35,38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Yandex Predictor API key",
                "Check_ID": "CKV_SECRET_72",
                "Regex": "(?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(t1\\.[A-Z0-9a-z_-]+[=]{0,2}\\.[A-Z0-9a-z_-]{86}[=]{0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"
            },
            {
                "Name": "Scalr API Token",
                "Check_ID": "CKV_SECRET_76",
                "Regex": "(?i)(?:scalr)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9a-zA-Z.\\-_]{136})"
            },
            {
                "Name": "Scalr API Token",
                "Check_ID": "CKV_SECRET_76",
                "Regex": "(?i)(?:scalr)(?:.|[\\n\\r]){0,40}\\b(at\\-(?:[0-9a-z]{12,20}))\\b"
            },
            {
                "Name": "Webflow API Token",
                "Check_ID": "CKV_SECRET_75",
                "Regex": "(?i)(?:webflow)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA0-9]{64})\\b"
            },
            {
                "Name": "Vercel API Token",
                "Check_ID": "CKV_SECRET_74",
                "Regex": "(?i)(?:vercel)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9]{24})\\b"
            },
            {
                "Name": "Cloudflare API Credentials",
                "Check_ID": "CKV_SECRET_73",
                "Regex": "(?i)(?:cloudflare)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{40})\\b"
            },
            {
                "Name": "Telegram Bot Token",
                "Check_ID": "CKV_SECRET_68",
                "Regex": "(?i)(?:telegram)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9]{8,10}:[a-zA-Z0-9_-]{35})\\b"
            },
            {
                "Name": "Splunk User Credentials",
                "Check_ID": "CKV_SECRET_66",
                "Regex": "(?i)(?:splunk)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9A-Z]{22})\\b"
            },
            {
                "Name": "PagerDuty Authorization Token",
                "Check_ID": "CKV_SECRET_57",
                "Regex": "(?i)(?:pagerduty)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z]{1}\\+[a-zA-Z]{9}\\-[a-z]{2}\\-[a-z0-9]{5})\\b"
            },
            {
                "Name": "Notion Integration Token",
                "Check_ID": "CKV_SECRET_55",
                "Regex": "\\b(secret_[A-Za-z0-9]{43})\\b"
            },
            {
                "Name": "Jira Token",
                "Check_ID": "CKV_SECRET_51",
                "Regex": "(?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9]{24})\\b"
            },
            {
                "Name": "Jira Token",
                "Check_ID": "CKV_SECRET_51",
                "Regex": "(?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([\\w\\-\\.]+@(?:[\\w-]+\\.)+[\\w-]{2,4})\\b"
            },
            {
                "Name": "DigitalOcean Token",
                "Check_ID": "CKV_SECRET_34",
                "Regex": "(?i)(?:digitalocean)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{64})\\b"
            },
            {
                "Name": "Elastic Email Key",
                "Check_ID": "CKV_SECRET_40",
                "Regex": "(?i)(?:elastic)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{96})\\b"
            },
            {
                "Name": "FullStory API Key",
                "Check_ID": "CKV_SECRET_42",
                "Regex": "(?i)(?:fullstory)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9/+]{88})\\b"
            },
            {
                "Name": "Auth0 Key",
                "Check_ID": "CKV_SECRET_26",
                "Regex": "(?i)(?:auth0)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9_-]{32,60})\\b"
            },
            {
                "Name": "Buildkite Agent Token",
                "Check_ID": "CKV_SECRET_28",
                "Regex": "(?i)(?:buildkite)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9]{40})\\b"
            },
            {
                "Name": "CircleCI Personal Token",
                "Check_ID": "CKV_SECRET_29",
                "Regex": "(?i)(?:circle)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-fA-F0-9]{40})"
            }
        ]
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
            },
            {
                "incidentId": "BC_GIT_33",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Databricks Authentication Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_33",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_33",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(dsapi[a-h0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Databricks Authentication Token",
                "constructiveTitle": "Databricks Authentication Token",
                "pcPolicyId": "1979aa5f-0e33-4521-b7aa-0d7f18f298ca",
                "additionalPcPolicyIds":
                    [
                        "1979aa5f-0e33-4521-b7aa-0d7f18f298ca"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_34",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "DigitalOcean Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_34",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_34",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:digitalocean)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{64})\\b",
                "descriptiveTitle": "DigitalOcean Token",
                "constructiveTitle": "DigitalOcean Token",
                "pcPolicyId": "0a2d7460-9379-438d-9e0b-ab2976a826e0",
                "additionalPcPolicyIds":
                    [
                        "0a2d7460-9379-438d-9e0b-ab2976a826e0"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_35",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Discord Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_35",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_35",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{18})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Discord Token",
                "constructiveTitle": "Discord Token",
                "pcPolicyId": "b0e5f091-e7de-4d70-bbcf-3289a307c0eb",
                "additionalPcPolicyIds":
                    [
                        "b0e5f091-e7de-4d70-bbcf-3289a307c0eb"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_37",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "DroneCI Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_37",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_37",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:droneci)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "DroneCI Token",
                "constructiveTitle": "DroneCI Token",
                "pcPolicyId": "5686a696-223c-4b07-b5bf-427c780125a9",
                "additionalPcPolicyIds":
                    [
                        "5686a696-223c-4b07-b5bf-427c780125a9"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_40",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Elastic Email Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_40",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_40",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:elastic)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{96})\\b",
                "descriptiveTitle": "Elastic Email Key",
                "constructiveTitle": "Elastic Email Key",
                "pcPolicyId": "9567784e-cd7a-4fdf-9dc1-dcf90adbe6b1",
                "additionalPcPolicyIds":
                    [
                        "9567784e-cd7a-4fdf-9dc1-dcf90adbe6b1"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_41",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Fastly Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_41",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_41",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:fastly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Fastly Personal Token",
                "constructiveTitle": "Fastly Personal Token",
                "pcPolicyId": "96ca6d09-8c3e-47f2-b5d7-f5c2181fb387",
                "additionalPcPolicyIds":
                    [
                        "96ca6d09-8c3e-47f2-b5d7-f5c2181fb387"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_42",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "FullStory API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_42",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_42",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:fullstory)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9/+]{88})\\b",
                "descriptiveTitle": "FullStory API Key",
                "constructiveTitle": "FullStory API Key",
                "pcPolicyId": "84c57881-ad48-4959-8036-84c20699c43d",
                "additionalPcPolicyIds":
                    [
                        "84c57881-ad48-4959-8036-84c20699c43d"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_43",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "GitHub Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_43",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_43",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - gh[pousr]_[0-9a-zA-Z]{36}",
                "descriptiveTitle": "GitHub Token",
                "constructiveTitle": "GitHub Token",
                "pcPolicyId": "7864b6ac-5de9-4845-81f0-b9d9de32a0ca",
                "additionalPcPolicyIds":
                    [
                        "7864b6ac-5de9-4845-81f0-b9d9de32a0ca"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_44",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "GitLab Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_44",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_44",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - glpat-[0-9a-zA-Z\\-\\_]{20}",
                "descriptiveTitle": "GitLab Token",
                "constructiveTitle": "GitLab Token",
                "pcPolicyId": "14db94b2-590d-484b-98c5-b96aec2cfe97",
                "additionalPcPolicyIds":
                    [
                        "14db94b2-590d-484b-98c5-b96aec2cfe97"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_45",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Google Cloud Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_45",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_45",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(AIza[0-9A-Za-z\\\\-_]{35})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Google Cloud Keys",
                "constructiveTitle": "Google Cloud Keys",
                "pcPolicyId": "9d1b426e-4498-4660-a34f-8a43beb0a2b7",
                "additionalPcPolicyIds":
                    [
                        "9d1b426e-4498-4660-a34f-8a43beb0a2b7"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_46",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Grafana Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_46",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_46",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(eyJrIjoi[A-Za-z0-9]{70,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(glc_[A-Za-z0-9+/]{32,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(glsa_[A-Za-z0-9]{32}_[A-Fa-f0-9]{8})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Grafana Token",
                "constructiveTitle": "Grafana Token",
                "pcPolicyId": "b0a8cae4-c04e-4a99-a64e-b582d3e83000",
                "additionalPcPolicyIds":
                    [
                        "b0a8cae4-c04e-4a99-a64e-b582d3e83000"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_47",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Terraform Cloud API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_47",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_47",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}\n  - (?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}",
                "descriptiveTitle": "Terraform Cloud API Token",
                "constructiveTitle": "Terraform Cloud API Token",
                "pcPolicyId": "56b81a7c-1927-405e-be9e-c3213af08142",
                "additionalPcPolicyIds":
                    [
                        "56b81a7c-1927-405e-be9e-c3213af08142"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_48",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Heroku Platform Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_48",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_48",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:heroku)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Heroku Platform Key",
                "constructiveTitle": "Heroku Platform Key",
                "pcPolicyId": "ab6c1821-7b25-43d6-9ff0-ba300479c1ac",
                "additionalPcPolicyIds":
                    [
                        "ab6c1821-7b25-43d6-9ff0-ba300479c1ac"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_49",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "HubSpot API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_49",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_49",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:hubspot)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "HubSpot API Key",
                "constructiveTitle": "HubSpot API Key",
                "pcPolicyId": "bfdda3a2-e2d2-4bfb-ba7d-49466c108a88",
                "additionalPcPolicyIds":
                    [
                        "bfdda3a2-e2d2-4bfb-ba7d-49466c108a88"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_50",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Intercom Access Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_50",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_50",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:intercom)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{60})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Intercom Access Token",
                "constructiveTitle": "Intercom Access Token",
                "pcPolicyId": "1abf6697-5737-4067-8cbc-c060ca8cf331",
                "additionalPcPolicyIds":
                    [
                        "1abf6697-5737-4067-8cbc-c060ca8cf331"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_51",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Jira Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_51",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_51",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9]{24})\\b\n  - (?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([\\w\\-\\.]+@(?:[\\w-]+\\.)+[\\w-]{2,4})\\b",
                "descriptiveTitle": "Jira Token",
                "constructiveTitle": "Jira Token",
                "pcPolicyId": "afa159db-75a7-451c-9731-9a353c6e6a78",
                "additionalPcPolicyIds":
                    [
                        "afa159db-75a7-451c-9731-9a353c6e6a78"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_52",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "LaunchDarkly Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_52",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_52",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:launchdarkly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "LaunchDarkly Personal Token",
                "constructiveTitle": "LaunchDarkly Personal Token",
                "pcPolicyId": "90828b95-50f6-42ed-bc3f-4cc8a80e0250",
                "additionalPcPolicyIds":
                    [
                        "90828b95-50f6-42ed-bc3f-4cc8a80e0250"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_53",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Netlify Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_53",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_53",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:netlify)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40,46})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Netlify Token",
                "constructiveTitle": "Netlify Token",
                "pcPolicyId": "516fde21-67e9-4573-bfe7-41f6c5b8f5c0",
                "additionalPcPolicyIds":
                    [
                        "516fde21-67e9-4573-bfe7-41f6c5b8f5c0"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_54",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "New Relic Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_54",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_54",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRAK-[a-z0-9]{27})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRJS-[a-f0-9]{19})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "New Relic Key",
                "constructiveTitle": "New Relic Key",
                "pcPolicyId": "b2b74119-7057-4412-8b7d-fdf40e3cc916",
                "additionalPcPolicyIds":
                    [
                        "b2b74119-7057-4412-8b7d-fdf40e3cc916"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_55",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Notion Integration Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_55",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_55",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - \\b(secret_[A-Za-z0-9]{43})\\b",
                "descriptiveTitle": "Notion Integration Token",
                "constructiveTitle": "Notion Integration Token",
                "pcPolicyId": "8dcf5a77-4822-49f5-ab61-fcd7c748feea",
                "additionalPcPolicyIds":
                    [
                        "8dcf5a77-4822-49f5-ab61-fcd7c748feea"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_56",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Okta Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_56",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_56",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:okta)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{42})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Okta Token",
                "constructiveTitle": "Okta Token",
                "pcPolicyId": "ded6eeb0-ff9e-4455-bb8b-b9a5754fb758",
                "additionalPcPolicyIds":
                    [
                        "ded6eeb0-ff9e-4455-bb8b-b9a5754fb758"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_57",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "PagerDuty Authorization Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_57",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_57",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:pagerduty)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z]{1}\\+[a-zA-Z]{9}\\-[a-z]{2}\\-[a-z0-9]{5})\\b",
                "descriptiveTitle": "PagerDuty Authorization Token",
                "constructiveTitle": "PagerDuty Authorization Token",
                "pcPolicyId": "e66683fb-cce5-4b61-8a20-03fadc90d390",
                "additionalPcPolicyIds":
                    [
                        "e66683fb-cce5-4b61-8a20-03fadc90d390"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_58",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "PlanetScale Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_58",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_58",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(pscale_pw_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(pscale_tkn_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(pscale_oauth_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "PlanetScale Token",
                "constructiveTitle": "PlanetScale Token",
                "pcPolicyId": "d671864e-5c7b-423b-bfe2-2ede45e8d18a",
                "additionalPcPolicyIds":
                    [
                        "d671864e-5c7b-423b-bfe2-2ede45e8d18a"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_59",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Postman API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_59",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_59",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(PMAK-(?i)[a-f0-9]{24}\\-[a-f0-9]{34})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Postman API Key",
                "constructiveTitle": "Postman API Key",
                "pcPolicyId": "a183a84f-e1f0-4751-bdaa-b3b799ec3dd4",
                "additionalPcPolicyIds":
                    [
                        "a183a84f-e1f0-4751-bdaa-b3b799ec3dd4"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_60",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Pulumi Access Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_60",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_60",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(pul-[a-f0-9]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Pulumi Access Token",
                "constructiveTitle": "Pulumi Access Token",
                "pcPolicyId": "b2ec65ce-9bc0-463e-b8e2-92d38423183a",
                "additionalPcPolicyIds":
                    [
                        "b2ec65ce-9bc0-463e-b8e2-92d38423183a"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_61",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Python Package Index Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_61",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_61",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\\-_]{50,1000}",
                "descriptiveTitle": "Python Package Index Key",
                "constructiveTitle": "Python Package Index Key",
                "pcPolicyId": "ce61d4a3-bc17-494a-86f1-40d26fa73b1f",
                "additionalPcPolicyIds":
                    [
                        "ce61d4a3-bc17-494a-86f1-40d26fa73b1f"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_62",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "RapidAPI Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_62",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_62",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:rapidapi)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{50})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "RapidAPI Key",
                "constructiveTitle": "RapidAPI Key",
                "pcPolicyId": "1f01777e-9839-47c3-bd90-e840a464b17b",
                "additionalPcPolicyIds":
                    [
                        "1f01777e-9839-47c3-bd90-e840a464b17b"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_63",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Readme API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_63",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_63",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(rdme_[a-z0-9]{70})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Readme API Key",
                "constructiveTitle": "Readme API Key",
                "pcPolicyId": "be223514-2ba7-4937-80d8-2bc725d201c1",
                "additionalPcPolicyIds":
                    [
                        "be223514-2ba7-4937-80d8-2bc725d201c1"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_64",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "RubyGems API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_64",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_64",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(rubygems_[a-f0-9]{48})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "RubyGems API Key",
                "constructiveTitle": "RubyGems API Key",
                "pcPolicyId": "2a6b9d00-c551-4f66-865a-9e9950886745",
                "additionalPcPolicyIds":
                    [
                        "2a6b9d00-c551-4f66-865a-9e9950886745"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_65",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Sentry Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_65",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_65",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:sentry)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Sentry Token",
                "constructiveTitle": "Sentry Token",
                "pcPolicyId": "77cc76d6-34e9-4aea-8168-508e8c9b35bb",
                "additionalPcPolicyIds":
                    [
                        "77cc76d6-34e9-4aea-8168-508e8c9b35bb"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_66",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Splunk User Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_66",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_66",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:splunk)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9A-Z]{22})\\b",
                "descriptiveTitle": "Splunk User Credentials",
                "constructiveTitle": "Splunk User Credentials",
                "pcPolicyId": "6933e817-4991-4f9d-9bbf-b11bacfc8c29",
                "additionalPcPolicyIds":
                    [
                        "6933e817-4991-4f9d-9bbf-b11bacfc8c29"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_67",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Sumo Logic Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_67",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_67",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{14})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Sumo Logic Keys",
                "constructiveTitle": "Sumo Logic Keys",
                "pcPolicyId": "b5ba4ba2-8e01-4055-8086-e97a5ef5b598",
                "additionalPcPolicyIds":
                    [
                        "b5ba4ba2-8e01-4055-8086-e97a5ef5b598"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_68",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Telegram Bot Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_68",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_68",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:telegram)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9]{8,10}:[a-zA-Z0-9_-]{35})\\b",
                "descriptiveTitle": "Telegram Bot Token",
                "constructiveTitle": "Telegram Bot Token",
                "pcPolicyId": "bbe5b7b7-00e1-4c4f-8838-02d913a3df11",
                "additionalPcPolicyIds":
                    [
                        "bbe5b7b7-00e1-4c4f-8838-02d913a3df11"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_69",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Travis Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_69",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_69",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:travis)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{22})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Travis Personal Token",
                "constructiveTitle": "Travis Personal Token",
                "pcPolicyId": "9337a600-63d8-4b20-8492-6f6900ed2b6f",
                "additionalPcPolicyIds":
                    [
                        "9337a600-63d8-4b20-8492-6f6900ed2b6f"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_70",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Typeform API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_70",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_70",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:typeform)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(tfp_[a-z0-9\\-_\\.=]{59})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Typeform API Token",
                "constructiveTitle": "Typeform API Token",
                "pcPolicyId": "4d0f2321-6866-4fa9-b57c-1d7db2801acb",
                "additionalPcPolicyIds":
                    [
                        "4d0f2321-6866-4fa9-b57c-1d7db2801acb"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_71",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Vault Unseal Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_71",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_71",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(hvs\\.[a-z0-9_-]{90,100})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(hvb\\.[a-z0-9_-]{138,212})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Vault Unseal Key",
                "constructiveTitle": "Vault Unseal Key",
                "pcPolicyId": "d29f067e-31c9-44a2-b4e0-90a25b8595e1",
                "additionalPcPolicyIds":
                    [
                        "d29f067e-31c9-44a2-b4e0-90a25b8595e1"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_72",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Yandex Predictor API key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_72",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_72",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(YC[a-zA-Z0-9_\\-]{38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(AQVN[A-Za-z0-9_\\-]{35,38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(t1\\.[A-Z0-9a-z_-]+[=]{0,2}\\.[A-Z0-9a-z_-]{86}[=]{0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Yandex Predictor API key",
                "constructiveTitle": "Yandex Predictor API key",
                "pcPolicyId": "063f37de-6e7e-4d1f-8607-36502f9dfeaa",
                "additionalPcPolicyIds":
                    [
                        "063f37de-6e7e-4d1f-8607-36502f9dfeaa"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_74",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Vercel API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_74",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_74",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:vercel)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9]{24})\\b",
                "descriptiveTitle": "Vercel API Token",
                "constructiveTitle": "Vercel API Token",
                "pcPolicyId": "0e6cee83-8605-44a0-b53e-8410872d0cea",
                "additionalPcPolicyIds":
                    [
                        "0e6cee83-8605-44a0-b53e-8410872d0cea"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_75",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Webflow API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_75",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_75",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:webflow)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA0-9]{64})\\b",
                "descriptiveTitle": "Webflow API Token",
                "constructiveTitle": "Webflow API Token",
                "pcPolicyId": "7fc2545b-e320-4d5c-900c-d9218fe286c3",
                "additionalPcPolicyIds":
                    [
                        "7fc2545b-e320-4d5c-900c-d9218fe286c3"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_76",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Scalr API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_76",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_76",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:scalr)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9a-zA-Z.\\-_]{136})\n  - (?i)(?:scalr)(?:.|[\\n\\r]){0,40}\\b(at\\-(?:[0-9a-z]{12,20}))\\b",
                "descriptiveTitle": "Scalr API Token",
                "constructiveTitle": "Scalr API Token",
                "pcPolicyId": "6e65aa0b-c144-476e-90c4-1a8d1cd9e725",
                "additionalPcPolicyIds":
                    [
                        "6e65aa0b-c144-476e-90c4-1a8d1cd9e725"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_73",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Cloudflare API Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_73",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_73",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:cloudflare)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{40})\\b",
                "descriptiveTitle": "Cloudflare API Credentials",
                "constructiveTitle": "Cloudflare API Credentials",
                "pcPolicyId": "fbf7538b-dd40-4afe-a27d-81e118980598",
                "additionalPcPolicyIds":
                    [
                        "fbf7538b-dd40-4afe-a27d-81e118980598"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_36",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Doppler API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_36",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_36",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (dp\\.pt\\.)(?i)[a-z0-9]{43}",
                "descriptiveTitle": "Doppler API Key",
                "constructiveTitle": "Doppler API Key",
                "pcPolicyId": "009c3b4c-16cf-4c85-9b1d-4ab39fdbfb8b",
                "additionalPcPolicyIds":
                    [
                        "009c3b4c-16cf-4c85-9b1d-4ab39fdbfb8b"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_21",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Airtable API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_21",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_21",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:airtable)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{17})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Airtable API Key",
                "constructiveTitle": "Airtable API Key",
                "pcPolicyId": "8058279d-25be-4115-bd84-6b830faa3c5d",
                "additionalPcPolicyIds":
                    [
                        "8058279d-25be-4115-bd84-6b830faa3c5d"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_22",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Algolia Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_22",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_22",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:algolia)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Algolia Key",
                "constructiveTitle": "Algolia Key",
                "pcPolicyId": "1ea47a16-0199-4117-93f9-01de3fcdd814",
                "additionalPcPolicyIds":
                    [
                        "1ea47a16-0199-4117-93f9-01de3fcdd814"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_23",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Alibaba Cloud Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_23",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_23",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:alibaba)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{30})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Alibaba Cloud Keys",
                "constructiveTitle": "Alibaba Cloud Keys",
                "pcPolicyId": "34a51c97-a8be-444b-816b-06ff2c99b462",
                "additionalPcPolicyIds":
                    [
                        "34a51c97-a8be-444b-816b-06ff2c99b462"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_24",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Asana Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_24",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_24",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Asana Key",
                "constructiveTitle": "Asana Key",
                "pcPolicyId": "250a1587-69ae-4878-8a7c-6c300eb9132f",
                "additionalPcPolicyIds":
                    [
                        "250a1587-69ae-4878-8a7c-6c300eb9132f"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_25",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Atlassian Oauth2 Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_25",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_25",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:atlassian|confluence|jira)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Atlassian Oauth2 Keys",
                "constructiveTitle": "Atlassian Oauth2 Keys",
                "pcPolicyId": "550b4cdd-b107-4bd7-8397-a38b8e32f713",
                "additionalPcPolicyIds":
                    [
                        "550b4cdd-b107-4bd7-8397-a38b8e32f713"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_26",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Auth0 Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_26",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_26",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:auth0)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9_-]{32,60})\\b",
                "descriptiveTitle": "Auth0 Keys",
                "constructiveTitle": "Auth0 Keys",
                "pcPolicyId": "8ebec33d-9b5e-4a9d-8796-0da742b67bef",
                "additionalPcPolicyIds":
                    [
                        "8ebec33d-9b5e-4a9d-8796-0da742b67bef"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_27",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Bitbucket Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_27",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_27",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Bitbucket Keys",
                "constructiveTitle": "Bitbucket Keys",
                "pcPolicyId": "afcada96-ce49-4e3a-b05a-c72da1b68083",
                "additionalPcPolicyIds":
                    [
                        "afcada96-ce49-4e3a-b05a-c72da1b68083"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_28",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Buildkite Agent Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_28",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_28",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:buildkite)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9]{40})\\b",
                "descriptiveTitle": "Buildkite Agent Token",
                "constructiveTitle": "Buildkite Agent Token",
                "pcPolicyId": "b440bbd1-34e4-48dd-ae3d-89738d508ff3",
                "additionalPcPolicyIds":
                    [
                        "b440bbd1-34e4-48dd-ae3d-89738d508ff3"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_29",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "CircleCI Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_29",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_29",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:circle)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-fA-F0-9]{40})",
                "descriptiveTitle": "CircleCI Personal Token",
                "constructiveTitle": "CircleCI Personal Token",
                "pcPolicyId": "10fac584-5171-4acb-8fcf-818c48e93cd5",
                "additionalPcPolicyIds":
                    [
                        "10fac584-5171-4acb-8fcf-818c48e93cd5"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_30",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Codecov API key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_30",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_30",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:codecov)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Codecov API key",
                "constructiveTitle": "Codecov API key",
                "pcPolicyId": "d047a76c-6d7f-4281-bcb9-9e9c79b896d2",
                "additionalPcPolicyIds":
                    [
                        "d047a76c-6d7f-4281-bcb9-9e9c79b896d2"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_31",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Coinbase Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_31",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_31",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:coinbase)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Coinbase Keys",
                "constructiveTitle": "Coinbase Keys",
                "pcPolicyId": "d54bf289-817a-41bc-8f31-3502ab3db364",
                "additionalPcPolicyIds":
                    [
                        "d54bf289-817a-41bc-8f31-3502ab3db364"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_32",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Confluent Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_32",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_32",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Confluent Keys",
                "constructiveTitle": "Confluent Keys",
                "pcPolicyId": "720b664c-19cb-4e26-a6e5-1beb402734a5",
                "additionalPcPolicyIds":
                    [
                        "720b664c-19cb-4e26-a6e5-1beb402734a5"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_38",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Dropbox App Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_38",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_38",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{15})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(sl\\.[a-z0-9\\-=_]{135})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Dropbox App Credentials",
                "constructiveTitle": "Dropbox App Credentials",
                "pcPolicyId": "8f4d0292-8ddc-4505-a52d-3ce1280fc321",
                "additionalPcPolicyIds":
                    [
                        "8f4d0292-8ddc-4505-a52d-3ce1280fc321"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_39",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Dynatrace token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_39",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_39",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Dynatrace token",
                "constructiveTitle": "Dynatrace token",
                "pcPolicyId": "a4e5aa1e-94ba-4aa1-ab46-1f137b10110c",
                "additionalPcPolicyIds":
                    [
                        "a4e5aa1e-94ba-4aa1-ab46-1f137b10110c"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            }
        ]}
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/custom_regex_detector"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 8)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_detectors_initialization(self) -> None:
        bc_integration.customer_run_config_response = {'secretsPolicies': [
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
            },
            {
                "incidentId": "BC_GIT_33",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Databricks Authentication Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_33",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_33",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(dsapi[a-h0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Databricks Authentication Token",
                "constructiveTitle": "Databricks Authentication Token",
                "pcPolicyId": "1979aa5f-0e33-4521-b7aa-0d7f18f298ca",
                "additionalPcPolicyIds":
                    [
                        "1979aa5f-0e33-4521-b7aa-0d7f18f298ca"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_34",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "DigitalOcean Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_34",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_34",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:digitalocean)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{64})\\b",
                "descriptiveTitle": "DigitalOcean Token",
                "constructiveTitle": "DigitalOcean Token",
                "pcPolicyId": "0a2d7460-9379-438d-9e0b-ab2976a826e0",
                "additionalPcPolicyIds":
                    [
                        "0a2d7460-9379-438d-9e0b-ab2976a826e0"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_35",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Discord Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_35",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_35",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{18})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:discord)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Discord Token",
                "constructiveTitle": "Discord Token",
                "pcPolicyId": "b0e5f091-e7de-4d70-bbcf-3289a307c0eb",
                "additionalPcPolicyIds":
                    [
                        "b0e5f091-e7de-4d70-bbcf-3289a307c0eb"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_37",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "DroneCI Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_37",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_37",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:droneci)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "DroneCI Token",
                "constructiveTitle": "DroneCI Token",
                "pcPolicyId": "5686a696-223c-4b07-b5bf-427c780125a9",
                "additionalPcPolicyIds":
                    [
                        "5686a696-223c-4b07-b5bf-427c780125a9"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_40",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Elastic Email Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_40",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_40",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:elastic)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{96})\\b",
                "descriptiveTitle": "Elastic Email Key",
                "constructiveTitle": "Elastic Email Key",
                "pcPolicyId": "9567784e-cd7a-4fdf-9dc1-dcf90adbe6b1",
                "additionalPcPolicyIds":
                    [
                        "9567784e-cd7a-4fdf-9dc1-dcf90adbe6b1"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_41",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Fastly Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_41",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_41",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:fastly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Fastly Personal Token",
                "constructiveTitle": "Fastly Personal Token",
                "pcPolicyId": "96ca6d09-8c3e-47f2-b5d7-f5c2181fb387",
                "additionalPcPolicyIds":
                    [
                        "96ca6d09-8c3e-47f2-b5d7-f5c2181fb387"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_42",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "FullStory API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_42",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_42",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:fullstory)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9/+]{88})\\b",
                "descriptiveTitle": "FullStory API Key",
                "constructiveTitle": "FullStory API Key",
                "pcPolicyId": "84c57881-ad48-4959-8036-84c20699c43d",
                "additionalPcPolicyIds":
                    [
                        "84c57881-ad48-4959-8036-84c20699c43d"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_43",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "GitHub Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_43",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_43",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - gh[pousr]_[0-9a-zA-Z]{36}",
                "descriptiveTitle": "GitHub Token",
                "constructiveTitle": "GitHub Token",
                "pcPolicyId": "7864b6ac-5de9-4845-81f0-b9d9de32a0ca",
                "additionalPcPolicyIds":
                    [
                        "7864b6ac-5de9-4845-81f0-b9d9de32a0ca"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_44",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "GitLab Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_44",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_44",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - glpat-[0-9a-zA-Z\\-\\_]{20}",
                "descriptiveTitle": "GitLab Token",
                "constructiveTitle": "GitLab Token",
                "pcPolicyId": "14db94b2-590d-484b-98c5-b96aec2cfe97",
                "additionalPcPolicyIds":
                    [
                        "14db94b2-590d-484b-98c5-b96aec2cfe97"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_45",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Google Cloud Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_45",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_45",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(AIza[0-9A-Za-z\\\\-_]{35})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Google Cloud Keys",
                "constructiveTitle": "Google Cloud Keys",
                "pcPolicyId": "9d1b426e-4498-4660-a34f-8a43beb0a2b7",
                "additionalPcPolicyIds":
                    [
                        "9d1b426e-4498-4660-a34f-8a43beb0a2b7"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_46",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Grafana Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_46",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_46",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(eyJrIjoi[A-Za-z0-9]{70,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(glc_[A-Za-z0-9+/]{32,400}={0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(glsa_[A-Za-z0-9]{32}_[A-Fa-f0-9]{8})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Grafana Token",
                "constructiveTitle": "Grafana Token",
                "pcPolicyId": "b0a8cae4-c04e-4a99-a64e-b582d3e83000",
                "additionalPcPolicyIds":
                    [
                        "b0a8cae4-c04e-4a99-a64e-b582d3e83000"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_47",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Terraform Cloud API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_47",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_47",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}\n  - (?i)[a-z0-9]{14}\\.atlasv1\\.[a-z0-9\\-_=]{60,70}",
                "descriptiveTitle": "Terraform Cloud API Token",
                "constructiveTitle": "Terraform Cloud API Token",
                "pcPolicyId": "56b81a7c-1927-405e-be9e-c3213af08142",
                "additionalPcPolicyIds":
                    [
                        "56b81a7c-1927-405e-be9e-c3213af08142"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_48",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Heroku Platform Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_48",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_48",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:heroku)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Heroku Platform Key",
                "constructiveTitle": "Heroku Platform Key",
                "pcPolicyId": "ab6c1821-7b25-43d6-9ff0-ba300479c1ac",
                "additionalPcPolicyIds":
                    [
                        "ab6c1821-7b25-43d6-9ff0-ba300479c1ac"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_49",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "HubSpot API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_49",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_49",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:hubspot)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "HubSpot API Key",
                "constructiveTitle": "HubSpot API Key",
                "pcPolicyId": "bfdda3a2-e2d2-4bfb-ba7d-49466c108a88",
                "additionalPcPolicyIds":
                    [
                        "bfdda3a2-e2d2-4bfb-ba7d-49466c108a88"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_50",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Intercom Access Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_50",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_50",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:intercom)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{60})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Intercom Access Token",
                "constructiveTitle": "Intercom Access Token",
                "pcPolicyId": "1abf6697-5737-4067-8cbc-c060ca8cf331",
                "additionalPcPolicyIds":
                    [
                        "1abf6697-5737-4067-8cbc-c060ca8cf331"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_51",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Jira Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_51",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_51",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z-0-9]{24})\\b\n  - (?i)(?:jira)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([\\w\\-\\.]+@(?:[\\w-]+\\.)+[\\w-]{2,4})\\b",
                "descriptiveTitle": "Jira Token",
                "constructiveTitle": "Jira Token",
                "pcPolicyId": "afa159db-75a7-451c-9731-9a353c6e6a78",
                "additionalPcPolicyIds":
                    [
                        "afa159db-75a7-451c-9731-9a353c6e6a78"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_52",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "LaunchDarkly Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_52",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_52",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:launchdarkly)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "LaunchDarkly Personal Token",
                "constructiveTitle": "LaunchDarkly Personal Token",
                "pcPolicyId": "90828b95-50f6-42ed-bc3f-4cc8a80e0250",
                "additionalPcPolicyIds":
                    [
                        "90828b95-50f6-42ed-bc3f-4cc8a80e0250"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_53",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Netlify Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_53",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_53",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:netlify)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{40,46})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Netlify Token",
                "constructiveTitle": "Netlify Token",
                "pcPolicyId": "516fde21-67e9-4573-bfe7-41f6c5b8f5c0",
                "additionalPcPolicyIds":
                    [
                        "516fde21-67e9-4573-bfe7-41f6c5b8f5c0"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_54",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "New Relic Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_54",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_54",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRAK-[a-z0-9]{27})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:new-relic|newrelic|new_relic)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(NRJS-[a-f0-9]{19})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "New Relic Key",
                "constructiveTitle": "New Relic Key",
                "pcPolicyId": "b2b74119-7057-4412-8b7d-fdf40e3cc916",
                "additionalPcPolicyIds":
                    [
                        "b2b74119-7057-4412-8b7d-fdf40e3cc916"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_55",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Notion Integration Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_55",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_55",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - \\b(secret_[A-Za-z0-9]{43})\\b",
                "descriptiveTitle": "Notion Integration Token",
                "constructiveTitle": "Notion Integration Token",
                "pcPolicyId": "8dcf5a77-4822-49f5-ab61-fcd7c748feea",
                "additionalPcPolicyIds":
                    [
                        "8dcf5a77-4822-49f5-ab61-fcd7c748feea"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_56",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Okta Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_56",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_56",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:okta)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{42})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Okta Token",
                "constructiveTitle": "Okta Token",
                "pcPolicyId": "ded6eeb0-ff9e-4455-bb8b-b9a5754fb758",
                "additionalPcPolicyIds":
                    [
                        "ded6eeb0-ff9e-4455-bb8b-b9a5754fb758"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_57",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "PagerDuty Authorization Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_57",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_57",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:pagerduty)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z]{1}\\+[a-zA-Z]{9}\\-[a-z]{2}\\-[a-z0-9]{5})\\b",
                "descriptiveTitle": "PagerDuty Authorization Token",
                "constructiveTitle": "PagerDuty Authorization Token",
                "pcPolicyId": "e66683fb-cce5-4b61-8a20-03fadc90d390",
                "additionalPcPolicyIds":
                    [
                        "e66683fb-cce5-4b61-8a20-03fadc90d390"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_58",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "PlanetScale Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_58",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_58",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(pscale_pw_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(pscale_tkn_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(pscale_oauth_(?i)[a-z0-9=\\-_\\.]{32,64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "PlanetScale Token",
                "constructiveTitle": "PlanetScale Token",
                "pcPolicyId": "d671864e-5c7b-423b-bfe2-2ede45e8d18a",
                "additionalPcPolicyIds":
                    [
                        "d671864e-5c7b-423b-bfe2-2ede45e8d18a"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_59",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Postman API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_59",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_59",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(PMAK-(?i)[a-f0-9]{24}\\-[a-f0-9]{34})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Postman API Key",
                "constructiveTitle": "Postman API Key",
                "pcPolicyId": "a183a84f-e1f0-4751-bdaa-b3b799ec3dd4",
                "additionalPcPolicyIds":
                    [
                        "a183a84f-e1f0-4751-bdaa-b3b799ec3dd4"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_60",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Pulumi Access Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_60",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_60",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(pul-[a-f0-9]{40})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Pulumi Access Token",
                "constructiveTitle": "Pulumi Access Token",
                "pcPolicyId": "b2ec65ce-9bc0-463e-b8e2-92d38423183a",
                "additionalPcPolicyIds":
                    [
                        "b2ec65ce-9bc0-463e-b8e2-92d38423183a"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_61",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Python Package Index Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_61",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_61",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - pypi-AgEIcHlwaS5vcmc[A-Za-z0-9\\-_]{50,1000}",
                "descriptiveTitle": "Python Package Index Key",
                "constructiveTitle": "Python Package Index Key",
                "pcPolicyId": "ce61d4a3-bc17-494a-86f1-40d26fa73b1f",
                "additionalPcPolicyIds":
                    [
                        "ce61d4a3-bc17-494a-86f1-40d26fa73b1f"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_62",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "RapidAPI Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_62",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_62",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:rapidapi)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{50})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "RapidAPI Key",
                "constructiveTitle": "RapidAPI Key",
                "pcPolicyId": "1f01777e-9839-47c3-bd90-e840a464b17b",
                "additionalPcPolicyIds":
                    [
                        "1f01777e-9839-47c3-bd90-e840a464b17b"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_63",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Readme API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_63",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_63",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(rdme_[a-z0-9]{70})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Readme API Key",
                "constructiveTitle": "Readme API Key",
                "pcPolicyId": "be223514-2ba7-4937-80d8-2bc725d201c1",
                "additionalPcPolicyIds":
                    [
                        "be223514-2ba7-4937-80d8-2bc725d201c1"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_64",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "RubyGems API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_64",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_64",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(rubygems_[a-f0-9]{48})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "RubyGems API Key",
                "constructiveTitle": "RubyGems API Key",
                "pcPolicyId": "2a6b9d00-c551-4f66-865a-9e9950886745",
                "additionalPcPolicyIds":
                    [
                        "2a6b9d00-c551-4f66-865a-9e9950886745"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_65",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Sentry Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_65",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_65",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:sentry)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-f0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Sentry Token",
                "constructiveTitle": "Sentry Token",
                "pcPolicyId": "77cc76d6-34e9-4aea-8168-508e8c9b35bb",
                "additionalPcPolicyIds":
                    [
                        "77cc76d6-34e9-4aea-8168-508e8c9b35bb"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_66",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Splunk User Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_66",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_66",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:splunk)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9A-Z]{22})\\b",
                "descriptiveTitle": "Splunk User Credentials",
                "constructiveTitle": "Splunk User Credentials",
                "pcPolicyId": "6933e817-4991-4f9d-9bbf-b11bacfc8c29",
                "additionalPcPolicyIds":
                    [
                        "6933e817-4991-4f9d-9bbf-b11bacfc8c29"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_67",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Sumo Logic Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_67",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_67",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{14})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:sumo)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Sumo Logic Keys",
                "constructiveTitle": "Sumo Logic Keys",
                "pcPolicyId": "b5ba4ba2-8e01-4055-8086-e97a5ef5b598",
                "additionalPcPolicyIds":
                    [
                        "b5ba4ba2-8e01-4055-8086-e97a5ef5b598"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_68",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Telegram Bot Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_68",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_68",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:telegram)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9]{8,10}:[a-zA-Z0-9_-]{35})\\b",
                "descriptiveTitle": "Telegram Bot Token",
                "constructiveTitle": "Telegram Bot Token",
                "pcPolicyId": "bbe5b7b7-00e1-4c4f-8838-02d913a3df11",
                "additionalPcPolicyIds":
                    [
                        "bbe5b7b7-00e1-4c4f-8838-02d913a3df11"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_69",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Travis Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_69",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_69",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:travis)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{22})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Travis Personal Token",
                "constructiveTitle": "Travis Personal Token",
                "pcPolicyId": "9337a600-63d8-4b20-8492-6f6900ed2b6f",
                "additionalPcPolicyIds":
                    [
                        "9337a600-63d8-4b20-8492-6f6900ed2b6f"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_70",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Typeform API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_70",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_70",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:typeform)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(tfp_[a-z0-9\\-_\\.=]{59})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Typeform API Token",
                "constructiveTitle": "Typeform API Token",
                "pcPolicyId": "4d0f2321-6866-4fa9-b57c-1d7db2801acb",
                "additionalPcPolicyIds":
                    [
                        "4d0f2321-6866-4fa9-b57c-1d7db2801acb"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_71",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Vault Unseal Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_71",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_71",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b(hvs\\.[a-z0-9_-]{90,100})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b(hvb\\.[a-z0-9_-]{138,212})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Vault Unseal Key",
                "constructiveTitle": "Vault Unseal Key",
                "pcPolicyId": "d29f067e-31c9-44a2-b4e0-90a25b8595e1",
                "additionalPcPolicyIds":
                    [
                        "d29f067e-31c9-44a2-b4e0-90a25b8595e1"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_72",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Yandex Predictor API key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_72",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_72",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(YC[a-zA-Z0-9_\\-]{38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(AQVN[A-Za-z0-9_\\-]{35,38})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:yandex)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(t1\\.[A-Z0-9a-z_-]+[=]{0,2}\\.[A-Z0-9a-z_-]{86}[=]{0,2})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Yandex Predictor API key",
                "constructiveTitle": "Yandex Predictor API key",
                "pcPolicyId": "063f37de-6e7e-4d1f-8607-36502f9dfeaa",
                "additionalPcPolicyIds":
                    [
                        "063f37de-6e7e-4d1f-8607-36502f9dfeaa"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_74",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Vercel API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_74",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_74",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:vercel)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9]{24})\\b",
                "descriptiveTitle": "Vercel API Token",
                "constructiveTitle": "Vercel API Token",
                "pcPolicyId": "0e6cee83-8605-44a0-b53e-8410872d0cea",
                "additionalPcPolicyIds":
                    [
                        "0e6cee83-8605-44a0-b53e-8410872d0cea"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_75",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Webflow API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_75",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_75",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:webflow)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA0-9]{64})\\b",
                "descriptiveTitle": "Webflow API Token",
                "constructiveTitle": "Webflow API Token",
                "pcPolicyId": "7fc2545b-e320-4d5c-900c-d9218fe286c3",
                "additionalPcPolicyIds":
                    [
                        "7fc2545b-e320-4d5c-900c-d9218fe286c3"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_76",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Scalr API Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_76",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_76",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:scalr)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([0-9a-zA-Z.\\-_]{136})\n  - (?i)(?:scalr)(?:.|[\\n\\r]){0,40}\\b(at\\-(?:[0-9a-z]{12,20}))\\b",
                "descriptiveTitle": "Scalr API Token",
                "constructiveTitle": "Scalr API Token",
                "pcPolicyId": "6e65aa0b-c144-476e-90c4-1a8d1cd9e725",
                "additionalPcPolicyIds":
                    [
                        "6e65aa0b-c144-476e-90c4-1a8d1cd9e725"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_73",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Cloudflare API Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_73",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_73",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:cloudflare)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([A-Za-z0-9_-]{40})\\b",
                "descriptiveTitle": "Cloudflare API Credentials",
                "constructiveTitle": "Cloudflare API Credentials",
                "pcPolicyId": "fbf7538b-dd40-4afe-a27d-81e118980598",
                "additionalPcPolicyIds":
                    [
                        "fbf7538b-dd40-4afe-a27d-81e118980598"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_36",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Doppler API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_36",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_36",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (dp\\.pt\\.)(?i)[a-z0-9]{43}",
                "descriptiveTitle": "Doppler API Key",
                "constructiveTitle": "Doppler API Key",
                "pcPolicyId": "009c3b4c-16cf-4c85-9b1d-4ab39fdbfb8b",
                "additionalPcPolicyIds":
                    [
                        "009c3b4c-16cf-4c85-9b1d-4ab39fdbfb8b"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_21",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Airtable API Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_21",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_21",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:airtable)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{17})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Airtable API Key",
                "constructiveTitle": "Airtable API Key",
                "pcPolicyId": "8058279d-25be-4115-bd84-6b830faa3c5d",
                "additionalPcPolicyIds":
                    [
                        "8058279d-25be-4115-bd84-6b830faa3c5d"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_22",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Algolia Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_22",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_22",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:algolia)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Algolia Key",
                "constructiveTitle": "Algolia Key",
                "pcPolicyId": "1ea47a16-0199-4117-93f9-01de3fcdd814",
                "additionalPcPolicyIds":
                    [
                        "1ea47a16-0199-4117-93f9-01de3fcdd814"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_23",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Alibaba Cloud Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_23",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_23",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:alibaba)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{30})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)\\b((LTAI)(?i)[a-z0-9]{20})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Alibaba Cloud Keys",
                "constructiveTitle": "Alibaba Cloud Keys",
                "pcPolicyId": "34a51c97-a8be-444b-816b-06ff2c99b462",
                "additionalPcPolicyIds":
                    [
                        "34a51c97-a8be-444b-816b-06ff2c99b462"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_24",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Asana Key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_24",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_24",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:asana)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Asana Key",
                "constructiveTitle": "Asana Key",
                "pcPolicyId": "250a1587-69ae-4878-8a7c-6c300eb9132f",
                "additionalPcPolicyIds":
                    [
                        "250a1587-69ae-4878-8a7c-6c300eb9132f"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_25",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Atlassian Oauth2 Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_25",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_25",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:atlassian|confluence|jira)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Atlassian Oauth2 Keys",
                "constructiveTitle": "Atlassian Oauth2 Keys",
                "pcPolicyId": "550b4cdd-b107-4bd7-8397-a38b8e32f713",
                "additionalPcPolicyIds":
                    [
                        "550b4cdd-b107-4bd7-8397-a38b8e32f713"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_26",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Auth0 Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_26",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_26",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:auth0)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-zA-Z0-9_-]{32,60})\\b",
                "descriptiveTitle": "Auth0 Keys",
                "constructiveTitle": "Auth0 Keys",
                "pcPolicyId": "8ebec33d-9b5e-4a9d-8796-0da742b67bef",
                "additionalPcPolicyIds":
                    [
                        "8ebec33d-9b5e-4a9d-8796-0da742b67bef"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_27",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Bitbucket Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_27",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_27",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:bitbucket)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9=_\\-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Bitbucket Keys",
                "constructiveTitle": "Bitbucket Keys",
                "pcPolicyId": "afcada96-ce49-4e3a-b05a-c72da1b68083",
                "additionalPcPolicyIds":
                    [
                        "afcada96-ce49-4e3a-b05a-c72da1b68083"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_28",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Buildkite Agent Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_28",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_28",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:buildkite)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-z0-9]{40})\\b",
                "descriptiveTitle": "Buildkite Agent Token",
                "constructiveTitle": "Buildkite Agent Token",
                "pcPolicyId": "b440bbd1-34e4-48dd-ae3d-89738d508ff3",
                "additionalPcPolicyIds":
                    [
                        "b440bbd1-34e4-48dd-ae3d-89738d508ff3"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_29",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "CircleCI Personal Token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_29",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_29",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:circle)(?:.|[\\n\\r]){0,40}(?<!\\.)\\b([a-fA-F0-9]{40})",
                "descriptiveTitle": "CircleCI Personal Token",
                "constructiveTitle": "CircleCI Personal Token",
                "pcPolicyId": "10fac584-5171-4acb-8fcf-818c48e93cd5",
                "additionalPcPolicyIds":
                    [
                        "10fac584-5171-4acb-8fcf-818c48e93cd5"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_30",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Codecov API key",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_30",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_30",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:codecov)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{32})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Codecov API key",
                "constructiveTitle": "Codecov API key",
                "pcPolicyId": "d047a76c-6d7f-4281-bcb9-9e9c79b896d2",
                "additionalPcPolicyIds":
                    [
                        "d047a76c-6d7f-4281-bcb9-9e9c79b896d2"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_31",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Coinbase Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_31",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_31",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:coinbase)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9_-]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Coinbase Keys",
                "constructiveTitle": "Coinbase Keys",
                "pcPolicyId": "d54bf289-817a-41bc-8f31-3502ab3db364",
                "additionalPcPolicyIds":
                    [
                        "d54bf289-817a-41bc-8f31-3502ab3db364"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_32",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Confluent Keys",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_32",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_32",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{64})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:confluent)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{16})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Confluent Keys",
                "constructiveTitle": "Confluent Keys",
                "pcPolicyId": "720b664c-19cb-4e26-a6e5-1beb402734a5",
                "additionalPcPolicyIds":
                    [
                        "720b664c-19cb-4e26-a6e5-1beb402734a5"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_38",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Dropbox App Credentials",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_38",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_38",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{15})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}(sl\\.[a-z0-9\\-=_]{135})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Dropbox App Credentials",
                "constructiveTitle": "Dropbox App Credentials",
                "pcPolicyId": "8f4d0292-8ddc-4505-a52d-3ce1280fc321",
                "additionalPcPolicyIds":
                    [
                        "8f4d0292-8ddc-4505-a52d-3ce1280fc321"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            },
            {
                "incidentId": "BC_GIT_39",
                "category": "Secrets",
                "severity": "LOW",
                "incidentType": "Violation",
                "title": "Dynatrace token",
                "guideline": "https://docs.bridgecrew.io/docs/git_secrets_39",
                "laceworkViolationId": "",
                "prowlerCheckId": "",
                "checkovCheckId": "CKV_SECRET_39",
                "resourceTypes":
                    [
                        "*"
                    ],
                "provider": "Git",
                "remediationIds":
                    [],
                "conditionQuery": None,
                "customerName": None,
                "isCustom": False,
                "createdBy": None,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:dropbox)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{11}(AAAAAAAAAA)[a-z0-9\\-_=]{43})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)",
                "descriptiveTitle": "Dynatrace token",
                "constructiveTitle": "Dynatrace token",
                "pcPolicyId": "a4e5aa1e-94ba-4aa1-ab46-1f137b10110c",
                "additionalPcPolicyIds":
                    [
                        "a4e5aa1e-94ba-4aa1-ab46-1f137b10110c"
                    ],
                "frameworks":
                    [
                        "Git"
                    ],
                "pcSeverity": "LOW",
                "sourceIncidentId": None
            }
        ]}

        detector_obj = CustomRegexDetector()

        assert len(detector_obj.denylist) == 75
        assert len(detector_obj.regex_to_metadata) == 75

        for detector in detector_obj.regex_to_metadata.values():
            assert detector.get('Name')
            assert detector.get('Check_ID')
            assert detector.get('Regex')
