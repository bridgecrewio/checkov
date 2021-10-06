import itertools
import json
import os
import sys
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovJsonReport(unittest.TestCase):

    def test_terragoat_report(self):
        report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_terragoat.json')
        self.validate_report(os.path.abspath(report_path))

    def test_cfngoat_report(self):
        report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_cfngoat.json')
        self.validate_report(os.path.abspath(report_path))
        self.validate_check_in_report(report_path, "CKV2_AWS_26")

    def test_k8goat_report(self):
        report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_kubernetes-goat.json')
        self.validate_report(os.path.abspath(report_path))

    def test_k8goat_report(self):
        if not sys.platform.startswith('win'):
            report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_kubernetes-goat-helm.json')
            self.validate_report(os.path.abspath(report_path))

    def test_checkov_report_terragoat_with_skip(self):
        report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_terragoat_with_skip.json')
        checkov2_graph_findings = 0
        with open(report_path) as json_file:
            data = json.load(json_file)
            for check_result in data["results"]["passed_checks"]:
                self.assertNotEqual(check_result["check_id"], "CKV_AWS_33")
                self.assertNotEqual(check_result["check_id"], "CKV_AWS_41")
                if check_result["check_id"].startswith('CKV2'):
                    checkov2_graph_findings += 1
        self.assertGreater(checkov2_graph_findings, 5)

    def validate_report(self, report_path):
        with open(report_path) as json_file:
            data = json.load(json_file)
            if isinstance(data, list):
                for framework_report in data:
                    self.validate_report_not_empty(framework_report)
            else:
                self.validate_report_not_empty(data)

    def validate_report_not_empty(self, report):
        self.assertEqual(report["summary"]["parsing_errors"], 0,
                         f"expecting 0 parsing errors but got: {report['results']['parsing_errors']}")
        self.assertGreater(report["summary"]["failed"], 1,
                           f"expecting more than 1 failed checks, got: {report['summary']['failed']}")

    def validate_json_quiet(self):
        report_path = os.path.join(os.path.dirname(current_dir), 'checkov_report_cfngoat_quiet.json')
        with open(report_path) as json_file:
            data = json.load(json_file)
            self.assertTrue(data["results"]["failed_checks"])
            self.assertFalse(data["results"]["passed_checks"])
            self.assertTrue(data["summary"])

    def validate_check_in_report(self, report_path, check_id):
        with open(report_path) as json_file:
            data = json.load(json_file)[0]
        assert any(check["check_id"] == check_id for check in
                   itertools.chain(data["results"]["failed_checks"], data["results"]["passed_checks"]))


if __name__ == '__main__':
    unittest.main()
