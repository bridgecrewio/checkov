import unittest

from checkov.common.bridgecrew.integration_features.features.fixes_integration import FixesIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


class TestFixesIntegration(unittest.TestCase):
    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_fixes = False
        instance.platform_integration_configured = True

        fixes_integration = FixesIntegration(instance)

        self.assertTrue(fixes_integration.is_valid())

        instance.skip_fixes = True
        self.assertFalse(fixes_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(fixes_integration.is_valid())

        instance.skip_fixes = False
        self.assertFalse(fixes_integration.is_valid())

        fixes_integration.integration_feature_failures = True
        self.assertFalse(fixes_integration.is_valid())


if __name__ == '__main__':
    unittest.main()
