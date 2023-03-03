import os
import unittest
from json import JSONDecodeError
from pathlib import Path

from checkov.common.parsers.json import load
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCfnJson(unittest.TestCase):

    def test_successful_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = f'{current_dir}/success.json'
        cfn = load(test_files)
        self.assertEqual(cfn[0]['AWSTemplateFormatVersion'], '2010-09-09')
        Runner().run(None, files=[test_files], runner_filter=RunnerFilter())

    def test_fail_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = current_dir + "/fail.json"
        self.assertRaises(JSONDecodeError, load, test_files)

    def test_skip_tf_plan_file(self):
        # given
        test_file = Path(__file__).parent / "tfplan.json"

        # when
        report = Runner().run(None, files=[str(test_file)], runner_filter=RunnerFilter())

        # then
        self.assertEqual(0, len(report.parsing_errors))
        
    def test_triple_quotes_string(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = f'{current_dir}/success_triple_quotes_string.json'
        cfn = load(test_files)
        self.assertEqual(cfn[0]['Metadata']['AWS::CloudFormation::Interface']['ParameterLabels']['NewTrailLogFilePrefix']['default'], 'Log file prefix\n hello')
        Runner().run(None, files=[test_files], runner_filter=RunnerFilter())


if __name__ == '__main__':
    unittest.main()
