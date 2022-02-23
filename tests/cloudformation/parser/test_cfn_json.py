import os
import unittest
from json import JSONDecodeError
from pathlib import Path

from checkov.common.bridgecrew.severities import Severities, BcSeverities
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

    def test_collect_skip_comments_json(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(current_dir, 'more_skip.json')
        runner = Runner()
        runner.run(None, files=[file], runner_filter=RunnerFilter())

        resources = runner.context[file]['Resources']

        b = resources['Bucket1']
        self.assertEqual(len(b['skipped_checks']), 2)
        self.assertEqual(b['skipped_checks'][0]['id'], 'CKV_AWS_56')
        self.assertEqual(b['skipped_checks'][0]['suppress_comment'], 'No comment provided')
        self.assertEqual(b['skipped_checks'][1]['id'], 'CKV_AWS_54')
        self.assertEqual(b['skipped_checks'][1]['suppress_comment'], 'some comment')

        b = resources['Bucket2']
        self.assertEqual(len(b['skipped_checks']), 3)
        self.assertEqual(b['skipped_checks'][0]['id'], 'CKV_AWS_56')
        self.assertEqual(b['skipped_checks'][1]['id'], 'CKV_AWS_54')
        self.assertEqual(b['skipped_checks'][-1]['severity'], Severities[BcSeverities.HIGH])
        self.assertEqual(b['skipped_checks'][-1]['suppress_comment'], "high justification")


if __name__ == '__main__':
    unittest.main()
