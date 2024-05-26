import unittest

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.integration_features.features.suppressions_integration import SuppressionsIntegration
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

    def test_policy_v2_suppression(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            "ruleType": "policy",
            "checkovPolicyIds": ["CKV_AWS_79", "CKV_AWS_80"],
        }

        record1 = Record(check_id='CKV_AWS_79', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_80', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(suppressions_integration._check_suppression_v2(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression_v2(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression_v2(record3, suppression))

    def test_suppress_by_policy_BC_VUL_2(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Policy',
            'id': '73114538-553a-4401-9ab4-d720e773024a',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress policy package_scan',
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='BC_VUL_22', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))

    def test_suppress_by_policy_BC_VUL_1(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Policy',
            'id': 'efc9357e-5517-4407-818f-814e7cc341d1',
            'policyId': 'BC_VUL_1',
            'comment': 'test',
            'checkovPolicyId': 'BC_VUL_1'
        }

        record1 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
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

    def test_suppress_by_cve_accounts_with_repo_id_package_scan(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'some/repo'
        instance.source_id = f"customer_{instance.repo_id}"
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'CvesAccounts',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress by accounts',
            'cves': ['CVE-2021-44420', 'CVE-2021-45452'],
            'accountIds': ['customer_some/repo'],
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-44420'})
        record2 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-45452'})
        record3 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

    def test_suppress_by_cve_accounts_without_repo_id_package_scan(self):
        instance = BcPlatformIntegration()
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'CvesAccounts',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress by accounts',
            'cves': ['CVE-2021-44420', 'CVE-2021-45452'],
            'accountIds': ['some/repo'],
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-44420'})
        record2 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-45452'})
        record3 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

    def test_suppress_by_cve_accounts_with_repo_id_image_scan(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'some/repo'
        instance.source_id = f"customer_{instance.repo_id}"
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'CvesAccounts',
            'policyId': 'BC_VUL_1',
            'comment': 'suppress by accounts',
            'cves': ['CVE-2021-44420', 'CVE-2021-45452'],
            'accountIds': ['customer_some/repo', 'customer_second/repo'],
            'checkovPolicyId': 'BC_VUL_1'
        }

        record1 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-44420'})
        record2 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-45452'})
        record3 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

        # with not matching repo-id
        instance2 = BcPlatformIntegration()
        instance2.repo_id = 'wrong/repo'
        suppressions_integration = SuppressionsIntegration(instance2)
        suppressions_integration._init_repo_regex()

        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))

    def test_suppress_by_cve_accounts_without_repo_id_image_scan(self):
        instance = BcPlatformIntegration()
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'CvesAccounts',
            'policyId': 'BC_VUL_1',
            'comment': 'suppress by accounts',
            'cves': ['CVE-2021-44420', 'CVE-2021-45452'],
            'accountIds': ['some/repo', 'second/repo'],
            'checkovPolicyId': 'BC_VUL_1'
        }

        record1 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-44420'})
        record2 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-45452'})
        record3 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

    def test_supress_by_cve_for_package_scan(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'some/repo'
        instance.source_id = f"customer_{instance.repo_id}"
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress cve ',
            'accountIds': ['customer_some/repo'],
            'cves': [
                {'uuid': '90397534-a1a0-41bb-a552-acdd861df618', 'id': '/requirements.txt', 'cve': 'CVE-2022-35920'},
                {'uuid': '90397534-a1a0-41bb-a552-acdd861df699', 'id': '/requirements.txt', 'cve': 'CVE-2021-23727'}],
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='requirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        record2 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='requirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-23727'})
        record3 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='requirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})
        record4 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='notrequirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record4, suppression))

    def test_suppress_by_cve_with_empty_cves(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'repo/path'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress cve ',
            'cves': [],
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path='repo/path',
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))

    def test_supress_by_cve_for_package_scan_with_different_repo_id(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'some/repo'
        instance.source_id = f"customer_{instance.repo_id}"
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress cve ',
            'accountIds': ['customer_other/repo'],
            'cves': [
                {'uuid': '90397534-a1a0-41bb-a552-acdd861df618', 'id': '/requirements.txt', 'cve': 'CVE-2022-35920'},
                {'uuid': '90397534-a1a0-41bb-a552-acdd861df699', 'id': '/requirements.txt', 'cve': 'CVE-2021-23727'}],
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='requirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        record2 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='requirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-23727'})
        record3 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='requirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})
        record4 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='notrequirements.txt', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record4, suppression))

    def test_supress_by_cve_for_image_scan(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'some/repo'
        instance.source_id = f"customer_{instance.repo_id}"
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_1',
            'comment': 'suppress cve ',
            'accountIds': ['customer_some/repo'],
            'cves': [{'uuid': '90397534-a1a0-41bb-a552-acdd861df618', 'id': '/dockerfile/Dockerfile',
                      'cve': 'CVE-2022-35920'},
                     {'uuid': '90397534-a1a0-41bb-a552-acdd861df699', 'id': '/dockerfile/Dockerfile',
                      'cve': 'CVE-2021-23727'}],
            'checkovPolicyId': 'BC_VUL_1'
        }

        record1 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='path/to/some/repo/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        record2 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='path/to/some/repo/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-23727'})
        record3 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='path/to/some/repos/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})
        record4 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='path/to/some/repo/notdockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record4, suppression))

    def test_supress_by_cve_for_image_scan_with_different_repo_id(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'some/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_1',
            'comment': 'suppress cve ',
            'accountIds': ['other/repo'],
            'cves': [{'uuid': '90397534-a1a0-41bb-a552-acdd861df618', 'id': '/dockerfile/Dockerfile',
                      'cve': 'CVE-2022-35920'},
                     {'uuid': '90397534-a1a0-41bb-a552-acdd861df699', 'id': '/dockerfile/Dockerfile',
                      'cve': 'CVE-2021-23727'}],
            'checkovPolicyId': 'BC_VUL_1'
        }

        record1 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='other/repo/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        record2 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='other/repo/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-23727'})
        record3 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='other/repo/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})
        record4 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='other/repo/dockerfile/Dockerfile', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-45452'})

        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record4, suppression))

    def test_supress_by_cve_for_image_scan_without_accountIds(self):
        instance = BcPlatformIntegration()
        instance.repo_id = '/dockerfile/Dockerfile'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_1',
            'comment': 'suppress cve ',
            'cves': [{'uuid': '90397534-a1a0-41bb-a552-acdd861df618', 'id': '/dockerfile/Dockerfile',
                      'cve': 'CVE-2022-35920'},
                     {'uuid': '90397534-a1a0-41bb-a552-acdd861df699', 'id': '/dockerfile/Dockerfile',
                      'cve': 'CVE-2021-23727'}],
            'checkovPolicyId': 'BC_VUL_1'
        }

        record1 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path='/dockerfile/Dockerfile',
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        record2 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path='/dockerfile/Dockerfile',
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-23727'})
        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))

    def test_supress_by_cve_for_package_scan_without_accountIds(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'repo/path'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()

        suppression = {
            'suppressionType': 'Cves',
            'policyId': 'BC_VUL_2',
            'comment': 'suppress cve ',
            'cves': [{'uuid': '90397534-a1a0-41bb-a552-acdd861df618', 'id': 'repo/path',
                      'cve': 'CVE-2022-35920'},
                     {'uuid': '90397534-a1a0-41bb-a552-acdd861df699', 'id': 'repo/path',
                      'cve': 'CVE-2021-23727'}],
            'checkovPolicyId': 'BC_VUL_2'
        }

        record1 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path='repo/path',
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2022-35920'})
        record2 = Record(check_id='BC_VUL_2', check_name=None, check_result=None,
                         code_block=None, file_path='repo/path',
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'id': 'CVE-2021-23727'})
        self.assertFalse(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))

    def test_suppress_licenses_by_policy(self):
        instance = BcPlatformIntegration()
        suppressions_integration = SuppressionsIntegration(instance)

        suppression = {'suppressionType': 'Policy',
                       'policyId': 'BC_LIC_1',
                       'comment': 'test licenses suppressions by policy ',
                       'checkovPolicyId': 'BC_LIC_1'
                       }
        record1 = Record(check_id='BC_LIC_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'JSON'})
        record2 = Record(check_id='BC_LIC_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'GPL-1.0'})
        record3 = Record(check_id='BC_VUL_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'GPL-2.0'})
        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))

    def test_supress_licenses_by_type(self):
        instance = BcPlatformIntegration()
        suppressions_integration = SuppressionsIntegration(instance)

        suppression = {'suppressionType': 'LicenseType',
                       'policyId': 'BC_LIC_1',
                       'comment': 'test licenses suppressions by type ',
                       'licenseTypes': ['GPL-1.0', 'JSON'],
                       'checkovPolicyId': 'BC_LIC_1'
                       }
        record1 = Record(check_id='BC_LIC_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'JSON'})
        record2 = Record(check_id='BC_LIC_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'GPL-1.0'})
        record3 = Record(check_id='BC_LIC_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'GPL-2.0'})
        record4 = Record(check_id='BC_LIC_2', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None,
                         vulnerability_details={'license': 'GPL-1.0'})
        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record4, suppression))

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

    def test_repo_v2_suppression(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
        suppression = {
            "ruleType": "repository",
            "repositories": [
                {"repositoryName": "org/repo"},
                {"repositoryName": "not/valid"}
            ],
            "checkovPolicyIds": ["CKV_AWS_18", "CKV_AWS_19"],
        }

        # this is actually almost the same as a policy check, except we care about the repo name in the integration
        # record details do not matter, except policy ID
        record1 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_19', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(suppressions_integration._check_suppression_v2(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression_v2(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression_v2(record3, suppression))

        instance.repo_id = 'another/repo'
        self.assertFalse(suppressions_integration._check_suppression_v2(record1, suppression))

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

    def test_repo_v2_suppression_cli_repo(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
        suppression = {
            "ruleType": "repository",
            "repositories": [
                {"repositoryName": "1234_org/repo"},
                {"repositoryName": "1234_not/valid"}
            ],
            "checkovPolicyIds": ["CKV_AWS_18", "CKV_AWS_19"],
        }

        # this is actually almost the same as a policy check, except we care about the repo name in the integration
        # record details do not matter, except policy ID
        record1 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_19', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)

        self.assertTrue(suppressions_integration._check_suppression_v2(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression_v2(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression_v2(record3, suppression))

        instance.repo_id = 'another/repo'
        self.assertFalse(suppressions_integration._check_suppression_v2(record1, suppression))

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

        # cases for when the CWD of the process is outside the repo
        record4 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record4.file_path = '/terraform/aws/s3.tf'
        record4.repo_file_path = '/some/abs/path/to/terraform/aws/s3.tf'

        record5 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource='aws_s3_bucket.operations', evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record5.file_path = '\\terraform\\aws\\s3.tf'
        record5.repo_file_path = '/some/abs/path/to/terraform/aws/s3.tf'

        self.assertTrue(suppressions_integration._check_suppression(record1, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression(record3, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record4, suppression))
        self.assertTrue(suppressions_integration._check_suppression(record5, suppression))

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

    def test_file_v2_suppression_cli_repo(self):
        instance = BcPlatformIntegration()
        instance.repo_id = 'org/repo'
        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration._init_repo_regex()
        suppression = {
            "ruleType": "file",
            "files": [
                {
                    "repositoryName": "1234_org/repo",
                    "filePath": "test/file.txt"
                },
                {
                    "repositoryName": "1234_org/repo2",
                    "filePath": "/test/file2.txt"
                },
                {
                    "repositoryName": "1234_not/valid",
                    "filePath": "/test/file3.txt"
                }
            ],
            "checkovPolicyIds": ["CKV_AWS_18", "CKV_AWS_19"],
        }

        # this is actually almost the same as a policy check, except we care about the repo name in the integration
        # record details do not matter, except policy ID
        record1 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record1.repo_file_path = '/test/file.txt'
        record2 = Record(check_id='CKV_AWS_19', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2.repo_file_path = 'test/file.txt'  # should still match despite missing slash
        record3 = Record(check_id='CKV_AWS_18', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3.repo_file_path = '/test/file2.txt'
        record4 = Record(check_id='CKV_AWS_1', check_name=None, check_result=None,
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record4.repo_file_path = 'test/file.txt'

        self.assertTrue(suppressions_integration._check_suppression_v2(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression_v2(record2, suppression))
        self.assertFalse(suppressions_integration._check_suppression_v2(record3, suppression))  # right file, wrong repo
        self.assertFalse(suppressions_integration._check_suppression_v2(record4, suppression))

        record1.repo_file_path = '/test/file2.txt'
        record2.repo_file_path = 'test/file2.txt'
        instance.repo_id = 'org/repo2'  # now check the same thing but with a leading slash in the suppression file
        self.assertTrue(suppressions_integration._check_suppression_v2(record1, suppression))
        self.assertTrue(suppressions_integration._check_suppression_v2(record2, suppression))

        instance.repo_id = 'another/repo'
        self.assertFalse(suppressions_integration._check_suppression_v2(record1, suppression))

    def test_apply_suppressions_to_report(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)

        suppression = {
            "suppressionType": "Policy",
            "id": "7caab873-7400-47f9-8b3f-82b33d0463ed",
            "policyId": "BC_AWS_GENERAL_31",
            "comment": "No justification comment provided.",
            "checkovPolicyId": "CKV_AWS_79",
            "isV1": True
        }

        suppressions_integration.suppressions = {suppression['checkovPolicyId']: [suppression]}

        record1 = Record(check_id='CKV_AWS_79', check_name=None,
                         check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_1', check_name=None,
                         check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['multi_az']},
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
        self.assertEqual(report.skipped_checks[0].check_result['suppress_comment'], "No justification comment provided.")

    def test_apply_suppressions_to_report_with_v2(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)

        suppression = {
            "ruleType": "policy",
            "checkovPolicyIds": ["CKV_AWS_79", "CKV_AWS_80"],
            "isV1": False,
            "justificationComment": "comment"
        }

        suppressions_integration.suppressions_v2 = {id: [suppression] for id in suppression['checkovPolicyIds']}

        record1 = Record(check_id='CKV_AWS_79', check_name=None,
                         check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record2 = Record(check_id='CKV_AWS_1', check_name=None,
                         check_result={'result': CheckResult.FAILED, 'evaluated_keys': ['multi_az']},
                         code_block=None, file_path=None,
                         file_line_range=None,
                         resource=None, evaluations=None,
                         check_class=None, file_abs_path='.', entity_tags=None)
        record3 = Record(check_id='CKV_AWS_80', check_name=None,
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
        self.assertEqual(report.skipped_checks[0].check_result['suppress_comment'], "comment")

    def test_get_policy_level_suppressions(self):
        instance = BcPlatformIntegration()

        suppressions_integration = SuppressionsIntegration(instance)
        suppressions_integration.suppressions = {
            'CKV_AWS_252': [{'suppressionType': 'Policy', "isV1": True, 'id': '404088ed-4251-41ac-8dc1-45264af0c461',
                             'policyId': 'BC_AWS_GENERAL_175', 'creationDate': '2022-11-09T16:27:36.413Z',
                             'comment': 'Test2', 'checkovPolicyId': 'CKV_AWS_252'}],
            'CKV_AWS_36': [
                {'suppressionType': 'Policy', "isV1": True, 'id': 'b68013bc-2908-4c9a-969d-f1640d4aca11',
                 'policyId': 'BC_AWS_LOGGING_2',
                 'creationDate': '2022-11-09T16:11:58.435Z', 'comment': 'Testing', 'checkovPolicyId': 'CKV_AWS_36'}],
            'CKV_K8S_27': [
                {'suppressionType': 'Policy', "isV1": True, 'id': '271c1a79-2333-4a12-bf7d-55ec78468b94', 'policyId': 'BC_K8S_26',
                 'creationDate': '2022-12-08T08:00:04.561Z', 'comment': 'test checkov suppressions',
                 'checkovPolicyId': 'CKV_K8S_27'}],
            'acme_AWS_1668010000289': [
                {'suppressionType': 'Resources', "isV1": True, 'id': '5565e523-58da-4bc7-970e-c3fceef93ac1',
                 'policyId': 'acme_AWS_1668010000289', 'creationDate': '2022-11-09T16:28:50.887Z',
                 'comment': 'Testing', 'resources': [{'accountId': 'acme_cli_repo/testing-resources',
                                                      'resourceId': '/src/BC_AWS_LOGGING_7.tf:aws_cloudtrail.cloudtrail9'}],
                 'checkovPolicyId': 'acme_AWS_1668010000289'},
                {'suppressionType': 'Resources', "isV1": True, 'id': 'adf6f831-4393-4dcb-b345-2a14bf944267',
                 'policyId': 'acme_AWS_1668010000289', 'creationDate': '2022-11-09T16:28:50.951Z',
                 'comment': 'Testing', 'resources': [{'accountId': 'acme_cli_repo/testing-resources',
                                                      'resourceId': '/src/BC_AWS_LOGGING_7.tf:aws_cloudtrail.cloudtrail10'}],
                 'checkovPolicyId': 'acme_AWS_1668010000289'},
                {'suppressionType': 'Resources', "isV1": True, 'id': '86d88e69-5755-4e69-965b-f97fc26e784b',
                 'policyId': 'acme_AWS_1668010000289', 'creationDate': '2022-11-09T16:28:50.838Z',
                 'comment': 'Testing', 'resources': [{'accountId': 'acme_cli_repo/testing-resources',
                                                      'resourceId': '/src/BC_AWS_LOGGING_7.tf:aws_cloudtrail.cloudtrail8'}],
                 'checkovPolicyId': 'acme_AWS_1668010000289'}]}

        suppressions_integration.suppressions_v2 = {
            "CKV3_SAST_1": [{
                "ruleType": "policy",
                "isV1": False,
                "id": "1111",
                "policyIds": ["BC_SAST_1", "BC_SAST_2"]
            }],
            "CKV3_SAST_2": [
                {
                    "ruleType": "policy",
                    "isV1": False,
                    "id": "2222",
                    "policyIds": ["BC_SAST_3", "BC_SAST_2"]
                },
                {
                    "ruleType": "repository",
                    "isV1": False,
                    "id": "3333",
                    "policyIds": ["BC_SAST_1", "BC_SAST_3"]
                }
            ]
        }

        expected_suppressions = ['404088ed-4251-41ac-8dc1-45264af0c461', 'b68013bc-2908-4c9a-969d-f1640d4aca11',
                                 '271c1a79-2333-4a12-bf7d-55ec78468b94', '1111', '2222']
        policy_level_suppressions = suppressions_integration.get_policy_level_suppressions()
        self.assertEqual(expected_suppressions, list(policy_level_suppressions.keys()))
        self.assertEqual(policy_level_suppressions['404088ed-4251-41ac-8dc1-45264af0c461'], ['BC_AWS_GENERAL_175'])
        self.assertEqual(policy_level_suppressions['b68013bc-2908-4c9a-969d-f1640d4aca11'], ['BC_AWS_LOGGING_2'])
        self.assertEqual(policy_level_suppressions['271c1a79-2333-4a12-bf7d-55ec78468b94'], ['BC_K8S_26'])
        self.assertEqual(policy_level_suppressions['1111'], ["BC_SAST_1", "BC_SAST_2"])
        self.assertEqual(policy_level_suppressions['2222'], ["BC_SAST_3", "BC_SAST_2"])


if __name__ == '__main__':
    unittest.main()
