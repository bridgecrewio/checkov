import os
import unittest
from unittest import mock

from checkov.common.bridgecrew.bc_source import get_source_type
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


class TestBCApiUrl(unittest.TestCase):

    @mock.patch.dict(os.environ, {'BC_API_URL': 'foo'})
    def test_overriding_bc_api_url(self):
        instance = BcPlatformIntegration()
        self.assertEqual(instance.bc_api_url, "foo")

    @mock.patch.dict(os.environ, {'BC_SKIP_MAPPING': 'TRUE'})
    def test_skip_mapping(self):
        instance = BcPlatformIntegration()
        instance.setup_http_manager()
        instance.get_id_mapping()
        self.assertDictEqual({}, instance.ckv_to_bc_id_mapping)

    @mock.patch.dict(os.environ, {'BC_SKIP_MAPPING': 'FALSE'})
    def test_skip_mapping_false(self):
        instance = BcPlatformIntegration()
        instance.setup_http_manager()
        instance.get_id_mapping()
        self.assertIsNotNone(instance.ckv_to_bc_id_mapping)

    def test_should_upload(self):
        self.assertFalse(get_source_type('vscode').upload_results)
        self.assertTrue(get_source_type('cli').upload_results)
        self.assertFalse(get_source_type('xyz').upload_results)
        self.assertFalse(get_source_type(None).upload_results)


if __name__ == '__main__':
    unittest.main()
