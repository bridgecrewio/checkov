import unittest

from checkov.terraform.checks.resource.aws.EBSEncryption import check
from checkov.terraform.models.enums import CheckResult


class TestEBSEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf =  {'volume_id': ['${aws_ebs_volume.example.id}']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf =  {'volume_id': ['${aws_ebs_volume.example.id}'], 'encrypted': [True]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
