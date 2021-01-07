import unittest

from checkov.terraform.checks.resource.aws.SagemakerNotebookEncryption import check
from checkov.common.models.enums import CheckResult


class TestSagemakerNotebookEncryption(unittest.TestCase):

    def test_failure(self):
        resource_conf = {'name': ['my-notebook-instance'], 'role_arn': ['${aws_iam_role.role.arn}'],
                         'instance_type': ['ml.t2.medium']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['my-notebook-instance'], 'role_arn': ['${aws_iam_role.role.arn}'],
                         'instance_type': ['ml.t2.medium'], 'kms_key_id': ['foo']}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

if __name__ == '__main__':
    unittest.main()
