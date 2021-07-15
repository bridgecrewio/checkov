import os
import unittest
from unittest import mock

from checkov.common.bridgecrew.bc_source import should_upload_results
from checkov.common.bridgecrew.integration_features.features.suppressions_integration import SuppressionsIntegration
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

    @mock.patch.dict(os.environ, {'BC_SKIP_MAPPING': 'TRUE'})
    def test_skip_mapping(self):
        instance = BcPlatformIntegration()
        instance.setup_http_manager()
        instance.get_id_mapping()
        self.assertIsNone(instance.ckv_to_bc_id_mapping)

    @mock.patch.dict(os.environ, {'BC_SKIP_MAPPING': 'FALSE'})
    def test_skip_mapping_false(self):
        instance = BcPlatformIntegration()
        instance.setup_http_manager()
        instance.get_id_mapping()
        self.assertIsNotNone(instance.ckv_to_bc_id_mapping)

    def test_should_upload(self):
        self.assertFalse(should_upload_results('vscode'))
        self.assertTrue(should_upload_results('cli'))
        self.assertFalse(should_upload_results('xyz'))
        self.assertFalse(should_upload_results(None))


if __name__ == '__main__':
    unittest.main()
