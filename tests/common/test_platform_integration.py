import os
import unittest
from unittest import mock
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


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


if __name__ == '__main__':
    unittest.main()
