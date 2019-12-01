import unittest

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.resource_scanners.aws.SagemakerEncryption import scanner


class TestSagemakerEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['my-notebook-instance'], 'role_arn': ['${aws_iam_role.role.arn}'],
                         'instance_type': ['ml.t2.medium']}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.FAILURE, scan_result)

    def test_success(self):
        resource_conf = {'name': ['my-notebook-instance'], 'role_arn': ['${aws_iam_role.role.arn}'],
                         'instance_type': ['ml.t2.medium'], 'kms_key_id': ['foo']}
        scan_result = scanner.scan_resource_conf(conf=resource_conf)
        self.assertEqual(ScanResult.SUCCESS, scan_result)

if __name__ == '__main__':
    unittest.main()
