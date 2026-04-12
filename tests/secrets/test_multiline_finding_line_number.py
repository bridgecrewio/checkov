import os
import unittest


from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner
from tests.secrets.utils_for_test import _filter_reports_for_incident_ids


class TestMultilineFinding(unittest.TestCase):

    def test_multiline_finding(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/multiline_finding"
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
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  prerun:\n  - (?i)(?:algolia)\n  value:\n  - (?i)(?:algolia)(?:.|[\\n\\r]){0,80}([A-Za-z0-9]{32})\n",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()
        report = runner.run(root_folder=None,
                            files=[valid_dir_path + "/Dockerfile.mine"],
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test1"])
        self.assertEqual(len(interesting_failed_checks), 1)
        self.assertEqual(len(interesting_failed_checks[0].code_block), 1)
        self.assertEqual(len(interesting_failed_checks[0].code_block[0]), 2)
        self.assertEqual(interesting_failed_checks[0].code_block[0][0], 2)

    def test_multiline_two_secrets_same_check_id(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/multiline_finding"
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": "test_multiline_two",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test_multiline_two",
                "guideline": "test",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes": ["aws_instance"],
                "provider": "AWS",
                "remediationIds": [],
                "customerName": "test",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  multiline: true\n  prerun:\n  - (?i)(?:algolia)\n  value:\n  - (?i)(?:algolia)(?:.|[\\n\\r]){0,80}([A-Za-z0-9]{32})\n",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()
        report = runner.run(root_folder=None,
                            files=[valid_dir_path + "/Dockerfile.two_secrets"],
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test_multiline_two"])
        # Both secrets must be found
        self.assertEqual(len(interesting_failed_checks), 2)
        lines = sorted(c.file_line_range[0] for c in interesting_failed_checks)
        # First secret (b782...) is on line 2, second (c891...) is on line 7
        self.assertEqual(lines[0], 2)
        self.assertEqual(lines[1], 7)

    def test_single_line_two_secrets_same_check_id(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/single_line_finding"
        bc_integration.customer_run_config_response = {"secretsPolicies": [
            {
                "incidentId": "test_single_two",
                "category": "Secrets",
                "severity": "MEDIUM",
                "incidentType": "Violation",
                "title": "test_single_two",
                "guideline": "test",
                "laceworkViolationId": None,
                "prowlerCheckId": None,
                "checkovCheckId": None,
                "resourceTypes": ["aws_instance"],
                "provider": "AWS",
                "remediationIds": [],
                "customerName": "test",
                "isCustom": True,
                "code": "definition:\n  cond_type: secrets\n  value:\n  - (?i)(?:KEY)\\s*=\\s*'([A-Za-z0-9]{32})'\n",
                "descriptiveTitle": None,
                "constructiveTitle": None,
                "pcPolicyId": None,
                "additionalPcPolicyIds": None,
                "pcSeverity": None,
                "sourceIncidentId": None
            }
        ]}
        runner = Runner()
        report = runner.run(root_folder=None,
                            files=[valid_dir_path + "/secret.txt"],
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        interesting_failed_checks = _filter_reports_for_incident_ids(report.failed_checks, ["test_single_two"])
        # Both secrets must be found
        self.assertEqual(len(interesting_failed_checks), 2)
        lines = sorted(c.file_line_range[0] for c in interesting_failed_checks)
        # First secret is on line 1, second is on line 5
        self.assertEqual(lines[0], 1)
        self.assertEqual(lines[1], 5)
