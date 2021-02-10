import os
import unittest
from unittest import mock

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


if __name__ == '__main__':
    unittest.main()
