import os
import unittest
from pathlib import Path
from typing import Any, Dict, List

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.secrets.plugins.load_detectors import modify_secrets_policy_to_detectors, get_runnable_plugins
from checkov.secrets.runner import Runner
from tests.secrets.utils_for_test import _filter_reports_for_incident_ids


class TestLoadDetectors(unittest.TestCase):

    def test_get_runnable_plugins(self) -> None:
        policies_list: List[Dict[str, Any]] = [
            {
                "incidentId": "incident1",
                "category": "Secrets",
                "code": "definition:\n  cond_type: secrets\n  value:\n  - one_value\n",
                "title": "incident1",
            },
            {
                "incidentId": "incident2",
                "category": "Secrets",
                "code": "definition:\n  cond_type: secrets\n  value:\n  - H4sIAPmp12MC/8tIzcnJBwCGphA2BQAAAA==\n  is_runnable: true\n",
                "title": "incident2",
            },
            {
                "incidentId": "incident3",
                "category": "Secrets",
                "code": "",
                "title": "incident3",
            },
            {
                "incidentId": "incident4",
                "category": "Secrets",
                "code": "bad_code",
                "title": "incident4",
            },
            {
                "incidentId": "incident5",
                "category": "Secrets",
                "code": "definition:\n  cond_type: secrets\n  value:\n  - invalid\n  is_runnable: true\n",
                "title": "incident5",
            },
        ]
        runnables = get_runnable_plugins(policies_list)
        assert len(runnables) == 1
        assert runnables["incident2"] == 'hello'


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
                    "value": [],
                    "cond_type": "secrets"
                },
                "customerName": "lshind",
                "isCustom": True,
                "code": "",
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
                "conditionQuery": {
                    "value": ["abcdefg"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test1",
                "isCustom": True,
                "code": "",
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
                "conditionQuery": {
                    "value": [
                        "1234567"
                    ],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "",
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

    def test_custom_regex_detector(self):
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
                "conditionQuery": {
                    "value": ["(?:^|\W)HANA(?:$|\W)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test1",
                "isCustom": True,
                "code": None,
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
                "conditionQuery": {
                    "value": ["(?:^|\W)LIR(?:$|\W)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": None,
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
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 3)

    def test_non_entropy_take_precedence_over_entropy(self):
        # given: File with entropy secret and custom secret
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/custom_and_entropy"
        check_id = 'test1'
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": check_id,
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": check_id,
                "guideline": "test",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "conditionQuery": {
                    "value": ['test_pass =\s*"(.*?)"'],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test1",
                "isCustom": True,
                "code": None,
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()

        # when: Running the secrets runner on the file
        report = runner.run(root_folder=valid_dir_path, runner_filter=RunnerFilter(framework=['secrets'], enable_secret_scan_all_files=True))

        # then: Validating that the non-entropy is the one.
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1"])
        self.assertEqual(len(interesting_failed_checks), 1)
        self.assertEqual(interesting_failed_checks[0].check_id, check_id)

    def test_custom_regex_detector_value_str(self):
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
                "conditionQuery": {
                    "value": ["(?:^|\W)HANA(?:$|\W)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test1",
                "isCustom": True,
                "code": None,
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
                "conditionQuery": {
                    "value": ["(?:^|\W)LIR(?:$|\W)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": None,
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
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 3)

    def test_custom_regex_detector_in_custom_limit_characters(self):
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
                "conditionQuery": {
                    "value": ["(?i)(?:test)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "",
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
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 1)

    def test_custom_regex_detector_out_custom_limit_characters(self):
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
                "conditionQuery": {
                    "value": ["(?i)(?:out)(?:[0-9a-z\\-_\\t .]{0,20})(?:[\\s|']|[\\s|\"]){0,3}(?:=|>|:=|\\|\\|:|<=|=>|:)(?:'|\\\"|\\s|=|\\x60){0,5}([a-z0-9]{24})(?:['|\\\"|\\n|\\r|\\s|\\x60|;]|$)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": "",
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
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 0)

    def test_custom_regex_detector_skip_long_line(self):
        #  given
        valid_dir_path = Path(__file__).parent / "long_line_custom_regex_detector"
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
                "conditionQuery": {
                    "value": ["\w{20}"],  # this would definitely get a result, but should not, because of the line length
                    "cond_type": "secrets"
                },
                "resourceTypes": [],
                "provider": "AWS",
                "remediationIds": [],
                "customerName": "test2",
                "isCustom": True,
                "code": "",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}

        # when
        report = Runner().run(
            root_folder=str(valid_dir_path),
            runner_filter=RunnerFilter(
                framework=["secrets"],
                enable_secret_scan_all_files=True
            )
        )

        # then
        self.assertEqual(len(report.failed_checks), 0)

    def test_modify_secrets_policy_to_multiline_detectors(self) -> None:
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
                "customerName": "lshind",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - '{[\\s\\S]*}'",
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
                "incidentId": "test2",
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
                "customerName": "test2",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  value:\n  - '{[\\s\\S]*paz*}'",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            },
            {
                "incidentId": "test3",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test",
                "guideline": "test2",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "conditionQuery": {
                    "value": [
                        "1234567"
                    ],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test3",
                "isCustom": True,
                "code": "",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]
        detector_obj = modify_secrets_policy_to_detectors(policies_list)
        detectors_expected_result: List[Dict[str, Any]] = [
            {"Name": "test1", "Check_ID": "test1", "Regex": "{[\\s\\S]*}", "isMultiline": False},
            {"Name": "test2", "Check_ID": "test2", "Regex": "{[\\s\\S]*paz*}", "isMultiline": True},
            {"Name": "test3", "Check_ID": "test3", "Regex": "1234567", "isMultiline": False}
        ]
        detector_obj.sort(key=lambda detector: detector['Check_ID'])
        detectors_expected_result.sort(key=lambda detector: detector['Check_ID'])  # type: ignore
        assert all(
            True for x in range(0, len(detector_obj)) if
            detector_obj[x]['Check_ID'] == detectors_expected_result[x]['Check_ID'] and
            detector_obj[x]['isMultiline'] == detectors_expected_result[x]['isMultiline'])
        assert len(detectors_expected_result) == len(detector_obj)

    def test_custom_multiline_regex_detector(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/multiline_custom_regex_detector"
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
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  supported_files:\n  - .mine\n  value:\n  - '[\\s\\S]*HANA*'",
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
                "conditionQuery": {
                    "value": ["(?:^|\W)LIR(?:$|\W)"],
                    "cond_type": "secrets"
                },
                "resourceTypes":
                    [
                        "aws_instance"
                    ],
                "provider": "AWS",
                "remediationIds":
                    [],
                "customerName": "test2",
                "isCustom": True,
                "code": None,
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
                            runner_filter=RunnerFilter(
                                framework=['secrets'],
                                enable_secret_scan_all_files=True))
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 3)

    def test_custom_multiline_regex_detector_only_scan_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/multiline_custom_regex_detector"
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
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  supported_files:\n  - .mine\n  value:\n  - '[\\s\\S]*HANA*'",
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
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  supported_files:\n  - .mine\n  value:\n  - '[\\s\\S]*LIR*'",
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
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 2)

    def test_custom_multiline_regex_detector_only_supported_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/multiline_custom_regex_detector"
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
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  supported_files:\n  - .mine\n  value:\n  - '[\\s\\S]*HANA*'",
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
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  value:\n  - '[\\s\\S]*LIR*'",
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
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1", "test2"])
        self.assertEqual(len(interesting_failed_checks), 1)
