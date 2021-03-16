import unittest

from checkov.terraform.checks.utils.iam_terraform_document_to_policy_converter import \
    convert_terraform_conf_to_iam_policy


class TestIAMConverter(unittest.TestCase):

    def test_iam_converter(self):
        conf = {'version': ['2012-10-17'], 'statement': [{'actions': [['*']], 'resources': [['*']]}]}
        expected_result = {'version': ['2012-10-17'], 'Statement': [{'Action': ['*'], 'Resource': ['*'], 'Effect': 'Allow'}]}
        result = convert_terraform_conf_to_iam_policy(conf)
        self.assertDictEqual(result,expected_result)
        self.assertNotEqual(result,conf)



if __name__ == '__main__':
    unittest.main()
