import os
import unittest
from unittest import mock

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import PolicyMetadataIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.api_url, "foo")

    def test_overriding_pc_api_url(self):
        instance = BcPlatformIntegration()
        instance.setup_bridgecrew_credentials(
            repo_id="bridgecrewio/checkov",
            prisma_api_url="https://api0.prismacloud.io",
            source=get_source_type('disabled')
        )
        self.assertEqual(instance.api_url, "https://api0.prismacloud.io/bridgecrew")
        self.assertEqual(instance.prisma_api_url, "https://api0.prismacloud.io")

    def test_no_overriding_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.api_url, "https://www.bridgecrew.cloud")

    def test_skip_mapping_default(self):
        # Default is False so mapping is obtained
        instance = BcPlatformIntegration()
        instance.setup_http_manager()
        instance.get_public_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        self.assertIsNotNone(metadata_integration.check_metadata)
        self.assertGreater(len(metadata_integration.check_metadata), 0)

    def test_skip_mapping_true(self):
        instance = BcPlatformIntegration()
        instance.skip_download = True
        instance.setup_http_manager()
        instance.get_public_run_config()
        metadata_integration = PolicyMetadataIntegration(instance)
        metadata_integration.bc_integration = instance
        metadata_integration.pre_scan()
        self.assertIsNotNone(metadata_integration.check_metadata)
        self.assertDictEqual({}, metadata_integration.check_metadata)

    def test_should_upload(self):
        self.assertFalse(get_source_type('vscode').upload_results)
        self.assertTrue(get_source_type('cli').upload_results)
        self.assertTrue(get_source_type('xyz').upload_results)
        self.assertTrue(get_source_type(None).upload_results)


if __name__ == '__main__':
    unittest.main()
