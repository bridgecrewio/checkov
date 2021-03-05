import json
import os
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovJsonReport(unittest.TestCase):

    def test_terragoat_report(self):
        report_path = current_dir + "/../checkov_report_terragoat.json"
        self.validate_report(report_path)

    def test_cfngoat_report(self):
        report_path = current_dir + "/../checkov_report_cfngoat.json"
        self.validate_report(report_path)

    def test_k8goat_report(self):
        report_path = current_dir + "/../checkov_report_kubernetes-goat.json"
        self.validate_report(report_path)

    def test_k8goat_report(self):
        report_path = current_dir + "/../checkov_report_kubernetes-goat-helm.json"
        self.validate_report(report_path)

    def test_checkov_report_terragoat_with_skip(self):
        report_path = current_dir + "/../checkov_report_terragoat_with_skip.json"
        with open(report_path) as json_file:
            data = json.load(json_file)
            for check_result in data["results"]["passed_checks"]:
                self.assertNotEquals(check_result["check_id"], "CKV_AWS_33")
                self.assertNotEquals(check_result["check_id"], "CKV_AWS_41")

    def validate_report(self, report_path):
        with open(report_path) as json_file:
            data = json.load(json_file)
            self.assertEqual(data["summary"]["parsing_errors"], 0,
                             f"expecting 0 parsing errors but got: {data['results']['parsing_errors']}")
            self.assertGreater(data["summary"]["failed"], 1,
                               f"expecting more than 1 failed checks, got: {data['summary']['failed']}")

    def validate_json_quiet(self):
        report_path = current_dir + "/../checkov_report_cfngoat_quiet.json"
        with open(report_path) as json_file:
            data = json.load(json_file)
            self.assertTrue(data["results"]["failed_checks"])
            self.assertFalse(data["results"]["passed_checks"])
            self.assertTrue(data["summary"])

if __name__ == '__main__':
    unittest.main()
