import os
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovJsonReport(unittest.TestCase):

    def test_terragoat_report_dir(self):
        report_path = current_dir + "/../checkov_report_azuredir_api_key_terragoat.txt"
        self.validate_report(os.path.abspath(report_path))

    def test_terragoat_report_file(self):
        report_path = current_dir + "/../checkov_report_s3_singlefile_api_key_terragoat.txt"
        self.validate_report(os.path.abspath(report_path))

    def validate_report(self, report_path):
        platform_url_found = False
        with open(report_path) as f:
            if 'More details: https://www.bridgecrew.cloud/codeReview/' in f.read():
                platform_url_found = True
        self.assertTrue(platform_url_found, "when using api key, platform code review url should exist")


if __name__ == '__main__':
    unittest.main()
