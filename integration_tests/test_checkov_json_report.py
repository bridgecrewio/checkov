import unittest

import json
import os

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

    def validate_report(self, report_path):
        with open(report_path) as json_file:
            data = json.load(json_file)
            self.assertEqual(data["summary"]["parsing_errors"], 0, "expecting 0 parsing errors")
            self.assertGreater(data["summary"]["failed"], 1, "expecting more then 1 failed checks")


if __name__ == '__main__':
    unittest.main()
