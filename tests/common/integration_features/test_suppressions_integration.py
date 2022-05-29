import unittest

from checkov.common.bridgecrew.integration_features.features.suppressions_integration import SuppressionsIntegration
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report


class TestSuppressionsIntegration(unittest.TestCase):
    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True

        suppressions_integration = SuppressionsIntegration(instance)

        self.assertTrue(suppressions_integration.is_valid())

        instance.skip_download = True
        self.assertFalse(suppressions_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(suppressions_integration.is_valid())

        instance.skip_download = False
        self.assertFalse(suppressions_integration.is_valid())

        suppressions_integration.integration_feature_failures = True
        self.assertFalse(suppressions_integration.is_valid())

    def test_policy_id_regex(self):
        suppressions_integration = SuppressionsIntegration(BcPlatformIntegration())

        matching_ids = [
            'bcorg_aws_1234567891011',
            'bcORrg_aws_1234567891011',
            'bcORrg_AWS_1234567891011',
            'bcorg12_aws_1234567891011',
            'bcorgabcdefgh_azure_1234567891011',
            '0123456_azure_1234567891011'
        ]

        non_matching_ids = [
            'bcorg_aws_123456789101',
            'bcorg_aws123_1234567891011',
            'bcorg_1234567891011',
            'bcorgabcdefghazure_1234567891011',
            '_bcorg_aws_1234567891011',
        ]

        for id in matching_ids:
            self.assertIsNotNone(suppressions_integration.custom_policy_id_regex.match(id))

        for id in non_matching_ids:
            self.assertIsNone(suppressions_integration.custom_policy_id_regex.match(id))

    def test_repo_match(self):
        integration = BcPlatformIntegration()
        integration.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(integration)
        suppressions_integration._init_repo_regex()

        self.assertTrue(suppressions_integration._repo_matches('org/repo'))
        self.assertTrue(suppressions_integration._repo_matches('xyz_org/repo'))
        self.assertTrue(suppressions_integration._repo_matches('80001234_org/repo'))
        self.assertFalse(suppressions_integration._repo_matches('org/repo1'))
        self.assertFalse(suppressions_integration._repo_matches('xyz_org/repo1'))
        self.assertFalse(suppressions_integration._repo_matches('80001234_org/repo1'))

    def test_suppression_valid(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'

        metadata_integration.bc_to_ckv_id_mapping = {
            'BC_AWS_1': 'CKV_AWS_20'
        }
        metadata_integration.bc_integration = instance

        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "accountIds": [
                "org/repo"
            ]
        }

        self.assertTrue(suppressions_integration._suppression_valid_for_run(suppression))

        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "accountIds": [
                "bcorg_org/repo"
            ]
        }

        self.assertTrue(suppressions_integration._suppression_valid_for_run(suppression))

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

        self.assertTrue(suppressions_integration._suppression_valid_for_run(suppression))

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

        self.assertTrue(suppressions_integration._suppression_valid_for_run(suppression))

        suppression = {
            "suppressionType": "Policy",
            "policyId": "BC_AWS_1",
            "creationDate": 1602670330384,
            "comment": "No justification comment provided."
        }

        self.assertTrue(suppressions_integration._suppression_valid_for_run(suppression))

        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "accountIds": [
                "other/repo"
            ]
        }

        self.assertFalse(suppressions_integration._suppression_valid_for_run(suppression))

        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_1",
            "creationDate": 1608816140086,
            "comment": "No justification comment provided.",
            "accountIds": [
                "bcorg_other/repo"
            ]
        }

        self.assertFalse(suppressions_integration._suppression_valid_for_run(suppression))

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

        self.assertFalse(suppressions_integration._suppression_valid_for_run(suppression))

        # custom policy
        suppression = {
            "suppressionType": "Tags",
            "policyId": "bcorg_aws_1234567891011",
            "creationDate": 1610035761349,
            "comment": "No justification comment provided.",
            "tags": [
                {
                    "value": "test_1",
                    "key": "test_num"
                }
            ]
        }

        self.assertTrue(suppressions_integration._suppression_valid_for_run(suppression))

    def test_policy_suppression(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

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

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))

    def test_account_suppression(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
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

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))

    def test_account_suppression_cli_repo(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
        suppression = {
            "suppressionType": "Accounts",
            "policyId": "BC_AWS_S3_13",
            "comment": "testing checkov",
            "accountIds": ["bcorg_org/repo", "bcorg_not/valid"],
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

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))

    def test_resource_suppression(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
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

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

    def test_resource_suppression_cli_repo(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
        suppression = {
            "suppressionType": "Resources",
            "policyId": "BC_AWS_S3_13",
            "comment": "No justification comment provided.",
            "resources": [
                {
                    "accountId": "bcorg_org/repo",
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

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

    def test_tag_suppression(self):
        instance = BcPlatformIntegration()
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
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

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record3, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record4, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record5, suppression))

    def test_apply_suppressions_to_report(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)

        suppression = {
            "suppressionType": "Policy",
            "id": "7caab873-7400-47f9-8b3f-82b33d0463ed",
            "policyId": "BC_AWS_GENERAL_31",
            "comment": "No justification comment provided.",
            "checkovPolicyId": "CKV_AWS_79",
        }

        suppressions_integration.suppressions = {suppression['checkovPolicyId']: [suppression]}

        record1 = Record(check_id='CKV_AWS_79', check_name=None, check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_1', check_name=None, check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3 = Record(check_id='CKV_AWS_79', check_name=None,
                         check_result={'result': CheckResult.PASSED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record4 = Record(check_id='CKV_AWS_2', check_name=None,
                         check_result={'result': CheckResult.PASSED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        report = Report('terraform')
        report.add_record(record1)
        report.add_record(record2)
        report.add_record(record3)
        report.add_record(record4)

        suppressions_integration._apply_suppressions_to_report(report)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.failed_checks[0].check_id, 'CKV_AWS_1')
        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(report.passed_checks[0].check_id, 'CKV_AWS_2')
        self.assertEqual(len(report.skipped_checks), 2)


if __name__ == '__main__':
    unittest.main()
