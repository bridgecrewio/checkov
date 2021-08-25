import os
import unittest
from json import JSONDecodeError

from checkov.cloudformation.checks.resource.aws.ElasticacheReplicationGroupEncryptionAtTransitAuthToken import check
from checkov.cloudformation.parser import cfn_json
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCfnJson(unittest.TestCase):

    def test_successful_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = f'{current_dir}/success.json'
        cfn = cfn_json.load(test_files)
        self.assertEqual(cfn[0]['AWSTemplateFormatVersion'], '2010-09-09')
        Runner().run(None, files=[test_files],runner_filter=RunnerFilter())

    def test_fail_parsing(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files = current_dir + "/fail.json"
        self.assertRaises(JSONDecodeError, cfn_json.load,test_files)



if __name__ == '__main__':
    unittest.main()
