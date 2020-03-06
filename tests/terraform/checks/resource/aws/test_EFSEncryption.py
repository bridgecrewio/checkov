import unittest

from checkov.terraform.checks.resource.aws.EBSEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestEFSEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'creation_token': ["my-product"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf =  {'creation_token': ["my-product"], 'encrypted': [True], "kms_key_id": ["aws/efs"]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
