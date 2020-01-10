import unittest

from checkov.terraform.checks.data.aws.IAMParliament import check
from checkov.terraform.models.enums import CheckResult


class TestIAMParliament(unittest.TestCase):

    def test_success(self):
        data_conf = {'statement': [{'sid': ['1'], 'actions': [['s3:ListAllMyBuckets', 's3:GetBucketLocation']],
                                    'resources': [['arn:aws:s3:::*']]},
                                   {'actions': [['s3:ListBucket']], 'resources': [
                                       ['arn:*:s3:::*']]}]}

        scan_result = check.scan_data_conf(conf=data_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure(self):
        data_conf = {'statement': [{'sid': ['1'], 'actions': [['s3:ListAllMyBuckets', 's3:GetBucketLocation']],
                                    'resources': [['arn:aws:s3:::*']]}, {'actions': [['s3:ListBucket']],
                                                                         'resources': [
                                                                             ['arn:aws:s3:::${var.s3_bucket_name}']],
                                                                         'condition': [{'test': ['StringLike'],
                                                                                        'variable': ['s3:prefix'],
                                                                                        'values': [['', 'home/',
                                                                                                    'home/&{aws:username}/']]}]},
                                   {'actions': [['s4:*']], 'resources': [
                                       ['arn:aws:s4:::${var.s3_bucket_name}/home/&{aws:username}',
                                        'arn:aws:s4:::${var.s3_bucket_name}/home/&{aws:username}/*']]}]}

        scan_result = check.scan_data_conf(conf=data_conf)
        self.assertEqual(CheckResult.FAILED, scan_result[0])

    def test_failure_on_missing_property(self):
        resource_conf = {
            "minimum_password_length": [15],
            "require_lowercase_characters": [True],
            "require_numbers": [True],
            "require_uppercase_characters": [True],
            "require_symbols": [True],
            "allow_users_to_change_password": [True],
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()
