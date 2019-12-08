import unittest

from checkov.terraform.models.enums import CheckResult
from checkov.terraform.checks.resource.gcp.GoogleStorageBucketEncryption import check


class TestGoogleStorageBucketEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['my-bucket'],
                         'location': ['EU']
                         }

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf = {'name': ['my-bucket'],
                         'location': ['EU'],
                         'encryption': [{'default_kms_key_name': ['foo']}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.SUCCESS, scan_result)


if __name__ == '__main__':
    unittest.main()
