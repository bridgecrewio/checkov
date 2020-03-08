import unittest

from checkov.terraform.checks.resource.aws.ECRImageScanning import check
from checkov.common.models.enums import CheckResult


class TestECRImageScanning(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['bar'], 'image_tag_mutability': ['MUTABLE']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['bar'], 'image_tag_mutability': ['MUTABLE'],
                         'image_scanning_configuration': [{'scan_on_push': [True]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)


if __name__ == '__main__':
    unittest.main()
