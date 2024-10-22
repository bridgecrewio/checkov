import json
import os
import platform
import sys
import unittest

current_dir = os.path.dirname(os.path.realpath(__file__))


class TestCheckovJsonReport(unittest.TestCase):
    def test_terragoat_report_dir_api_key(self):
        report_path = os.path.join(current_dir, '..', 'checkov_report_azuredir_api_key_terragoat.txt')
        self.validate_report(os.path.abspath(report_path))

    def test_terragoat_report_dir_no_upload_api_key(self):
        report_path = os.path.join(current_dir, '..', 'checkov_report_azuredir_api_key_terragoat_no_upload.txt')
        self.validate_report(os.path.abspath(report_path), False)

    def test_terragoat_report_file_api_key(self):
        report_path = os.path.join(current_dir, '..', 'checkov_report_s3_singlefile_api_key_terragoat.txt')
        self.validate_report(os.path.abspath(report_path))

    def validate_report(self, report_path, url_should_exist=True):
        if sys.version_info[1] == 8 and platform.system() == 'Linux':
            platform_url_found = False
            with open(report_path) as f:
                if 'More details: https://app0.prismacloud.io/projects?' in f.read():
                    platform_url_found = True
            self.assertEqual(platform_url_found, url_should_exist, "when using api key and not --skip-results-upload, platform code review url should exist")

    def test_bitbucket_pipelines_report_api_key(self):
        report_path = os.path.join(current_dir, '..', 'checkov_report_bitbucket_pipelines_cve.json')
        # the below condition exist because checkov_report_bitbucket_pipelines_cve.json is
        # generated only on Linux with Python 3.8 - see prepare_data.sh script
        if sys.version_info[1] == 8 and platform.system() == 'Linux':
            with open(report_path, encoding='utf-8') as f:
                report = json.load(f)
                self.assertGreaterEqual(len(report), 1,
                                        "expecting to have one report at least - bitbucket_pipelines ")
                bitbucket_pipelines_actions_report_exists = False
                if report["check_type"] == "bitbucket_pipelines":
                    bitbucket_pipelines_actions_report_exists = True
                    self.assertGreaterEqual(report['summary']['failed'], 1)

                self.assertTrue(bitbucket_pipelines_actions_report_exists)


if __name__ == '__main__':
    unittest.main()
