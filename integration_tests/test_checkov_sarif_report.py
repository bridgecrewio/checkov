import json
import os
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovSarifReport(unittest.TestCase):

    def test_terragoat_report(self):
        report_path = os.path.join(os.path.dirname(current_dir), 'results.sarif')
        self.validate_report(os.path.abspath(report_path))

    def validate_report(self, report_path):
        with open(report_path) as json_file:
            data = json.load(json_file)
            if isinstance(data, list):
                for framework_report in data:
                    self.validate_report_not_empty(framework_report)
            else:
                self.validate_report_not_empty(data)

    def validate_report_not_empty(self, report):
        self.assertEqual(report["runs"][0]['tool']['driver']['name'], "Checkov")
        self.assertGreater(len(report["runs"][0]['results']), 1,
                           "expecting more than 1 failed checks")


if __name__ == '__main__':
    unittest.main()
