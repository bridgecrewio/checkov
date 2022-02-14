import os
import unittest
from unittest import mock

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.api_url, "foo")

    def test_overriding_pc_api_url(self):
        instance = BcPlatformIntegration()
        instance.setup_bridgecrew_credentials(
            repo_id="bridgecrewio/checkov"
            prisma_api_url="https://api0.prismacloud.io"
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
        instance.get_id_mapping()
        self.assertIsNotNone(instance.ckv_to_bc_id_mapping)

    def test_skip_mapping_true(self):
        instance = BcPlatformIntegration()
        instance.bc_skip_mapping = True
        instance.setup_http_manager()
        instance.get_id_mapping()
        self.assertDictEqual({}, instance.ckv_to_bc_id_mapping)

    def test_should_upload(self):
        self.assertFalse(get_source_type('vscode').upload_results)
        self.assertTrue(get_source_type('cli').upload_results)
        self.assertTrue(get_source_type('xyz').upload_results)
        self.assertTrue(get_source_type(None).upload_results)


if __name__ == '__main__':
    unittest.main()
