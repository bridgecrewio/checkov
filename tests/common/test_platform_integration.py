import os
import unittest
from unittest import mock
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.output.record import Record


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.bc_api_url, "foo")

    @mock.patch.dict(os.environ, {'BC_SOURCE': 'foo'})
    def test_overriding_bc_source(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.bc_source, "foo")

    def test_default_bc_source(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.bc_source, "cli")

    def test_suppression_valid(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        instance.bc_id_mapping = {
            'BC_AWS_1': 'CKV_AWS_20'
        }

        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "accountIds": [
                "org/repo"
            ]
        }

        self.assertTrue(instance._suppression_valid(suppression))

        suppression = {
            "suppressionType": "Resources",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "resources": {
                "accountId": "org/repo",
                "resourceId": "/s3.tf"
            }
        }

        self.assertTrue(instance._suppression_valid(suppression))

        suppression = {
            "suppressionType": "Tags",
            "policyId": "BC_AWS_1",
            "creationDate": 1610035761349,
            "comment": "No justification comment provided.",
            "tags": [
                {
                    "value": "test_1",
                    "key": "test_num"
                }
            ]
        }

        self.assertTrue(instance._suppression_valid(suppression))

        suppression = {
            "suppressionType": "Policy",
            "policyId": "BC_AWS_1",
            "creationDate": 1602670330384,
            "comment": "No justification comment provided."
        }

        self.assertTrue(instance._suppression_valid(suppression))

        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "accountIds": [
                "other/repo"
            ]
        }

        self.assertFalse(instance._suppression_valid(suppression))

        suppression = {
            "suppressionType": "Tags",
            "policyId": "NOT_A_POLICY",
            "creationDate": 1610035761349,
            "comment": "No justification comment provided.",
            "tags": [
                {
                    "value": "test_1",
                    "key": "test_num"
                }
            ]
        }

        self.assertFalse(instance._suppression_valid(suppression))

    def test_policy_suppression(self):
        instance = BcPlatformIntegration()
        suppression = {
            "suppressionType": "Policy",
            "id": "7caab873-7400-47f9-8b3f-82b33d0463ed",
            "policyId": "BC_AWS_GENERAL_31",
            "comment": "No justification comment provided.",
            "checkovPolicyId": "CKV_AWS_79",
        }

        record1 = Record(check_id='CKV_AWS_79', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(instance.check_suppression(record1, suppression))
        self.assertFalse(instance.check_suppression(record2, suppression))

    def test_account_suppression(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_S3_13",
            "comment": "testing checkov",
            "accountIds": ["org/repo", "not/valid"],
            "checkovPolicyId": "CKV_AWS_18",
        }

        record1 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(instance.check_suppression(record1, suppression))
        self.assertFalse(instance.check_suppression(record2, suppression))

    def test_resource_suppression(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppression = {
            "suppressionType": "Resources",
            "policyId": "BC_AWS_S3_13",
            "comment": "No justification comment provided.",
            "resources": [
                {
                    "accountId": "org/repo",
                    "resourceId": "/terraform/aws/s3.tf:aws_s3_bucket.operations",
                }
            ],
            "checkovPolicyId": "CKV_AWS_18",
        }

        record1 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path=',.', entity_tags=None)
        record1.repo_file_path = '/terraform/aws/s3.tf'
        record2 = Record(check_id='CKV_AWS_13', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.no', evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2.repo_file_path = '/terraform/aws/s3.tf'
        record3 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3.repo_file_path = '/terraform/aws/s3.tf'

        self.assertTrue(instance.check_suppression(record1, suppression))
        self.assertFalse(instance.check_suppression(record2, suppression))
        self.assertFalse(instance.check_suppression(record3, suppression))

    def test_tag_suppression(self):
        instance = BcPlatformIntegration()
        suppression = {
            "suppressionType": "Tags",
            "policyId": "BC_AWS_S3_16",
            "comment": "No justification comment provided.",
            "tags": [
                {
                    "value": "value1",
                    "key": "tag1"
                },
                {
                    "value": "value2",
                    "key": "tag2"
                }
            ],
            "checkovPolicyId": "CKV_AWS_21",
        }

        record1 = Record(check_id='CKV_AWS_21', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path=',.',
                         entity_tags={
                             'tag1': 'value1'
                         })
        record2 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.no', evaluations=None,
                         check_class=None, file_abs_path='.',
                         entity_tags={
                             'tag1': 'value1'
                         })
        record3 = Record(check_id='CKV_AWS_21', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path='.',
                         entity_tags={
                             'tag1': 'value2222',
                             'tag2': 'value2'
                         })
        record4 = Record(check_id='CKV_AWS_21', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path='.',
                         entity_tags={
                             'tag1': 'value2222',
                             'tag2': 'value1111'
                         })
        record5 = Record(check_id='CKV_AWS_21', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(instance.check_suppression(record1, suppression))
        self.assertFalse(instance.check_suppression(record2, suppression))
        self.assertTrue(instance.check_suppression(record3, suppression))
        self.assertFalse(instance.check_suppression(record4, suppression))
        self.assertFalse(instance.check_suppression(record5, suppression))

        if __name__ == '__main__':
            unittest.main()
