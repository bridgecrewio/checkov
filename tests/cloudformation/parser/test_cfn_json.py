import os
import unittest
from json import JSONDecodeError

from checkov.cloudformation.checks.resource.aws.ElasticacheReplicationGroupEncryptionAtTransitAuthToken import (
    check,
)
from checkov.cloudformation.parser import cfn_json
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCfnJson(unittest.TestCase):
    def test_successful_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = f"{current_dir}/success.json"
        cfn = cfn_json.load(test_files)
        self.assertEqual(cfn[0]["AWSTemplateFormatVersion"], "2010-09-09")
        Runner().run(None, files=[test_files], runner_filter=RunnerFilter())

    def test_fail_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = current_dir + "/fail.json"
        self.assertRaises(JSONDecodeError, cfn_json.load, test_files)


if __name__ == "__main__":
    unittest.main()


#
#
# from six import StringIO
# from mock import patch
#
# class TestCfnJson(BaseTestCase):
#     """Test JSON Parsing """
#
#     def setUp(self):
#         """ SetUp template object"""
#         self.rules = RulesCollection(include_experimental=True)
#         rulesdirs = [DEFAULT_RULESDIR]
#         for rulesdir in rulesdirs:
#             self.rules.create_from_directory(rulesdir)
#
#         self.filenames = {
#             "config_rule": {
#                 "filename": 'test/fixtures/templates/quickstart/config-rules.json',
#                 "failures": 6
#             },
#             "iam": {
#                 "filename": 'test/fixtures/templates/quickstart/iam.json',
#                 "failures": 4
#             },
#             "nat_instance": {
#                 "filename": 'test/fixtures/templates/quickstart/nat-instance.json',
#                 "failures": 2
#             },
#             "vpc_management": {
#                 "filename": 'test/fixtures/templates/quickstart/vpc-management.json',
#                 "failures": 35
#             },
#             "vpc": {
#                 "filename": 'test/fixtures/templates/quickstart/vpc.json',
#                 "failures": 40
#             },
#             "poller": {
#                 "filename": 'test/fixtures/templates/public/lambda-poller.json',
#                 "failures": 1
#             }
#         }
#
#     def test_success_parse(self):
#         """Test Successful JSON Parsing"""
#         for _, values in self.filenames.items():
#             filename = values.get('filename')
#             failures = values.get('failures')
#
#             template = cfnlint.decode.cfn_json.load(filename)
#             cfn = Template(filename, template, ['us-east-1'])
#
#             matches = []
#             matches.extend(self.rules.run(filename, cfn))
#             assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
#                 failures, len(matches), filename)
#
#     def test_success_escape_character(self):
#         """Test Successful JSON Parsing"""
#         failures = 1
#         filename = 'test/fixtures/templates/good/decode/parsing.json'
#         template = cfnlint.decode.cfn_json.load(filename)
#         cfn = Template(filename, template, ['us-east-1'])
#
#         matches = []
#         matches.extend(self.rules.run(filename, cfn))
#         assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
#             failures, len(matches), filename)
#
#     def test_success_parse_stdin(self):
#         """Test Successful JSON Parsing through stdin"""
#         for _, values in self.filenames.items():
#             filename = '-'
#             failures = values.get('failures')
#             with open(values.get('filename'), 'r') as fp:
#                 file_content = fp.read()
#             with patch('sys.stdin', StringIO(file_content)):
#
#                 template = cfnlint.decode.cfn_json.load(filename)
#                 cfn = Template(filename, template, ['us-east-1'])
#
#                 matches = []
#                 matches.extend(self.rules.run(filename, cfn))
#                 assert len(matches) == failures, 'Expected {} failures, got {} on {}'.format(
#                     failures, len(matches), values.get('filename'))
#
#     def test_fail_run(self):
#         """Test failure run"""
#
#         filename = 'test/fixtures/templates/bad/json_parse.json'
#
#         try:
#             template = cfnlint.decode.cfn_json.load(filename)
#         except cfnlint.decode.cfn_json.JSONDecodeError:
#             assert(True)
#             return
#
#         assert(False)
