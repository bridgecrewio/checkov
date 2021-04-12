import os
import unittest
from unittest import mock

from checkov.common.bridgecrew.integration_features.features.twistlock_integration import TwistLockIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.output.record import Record


class TestSuppressionsIntegration(unittest.TestCase):
    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.platform_integration_configured = True
        twistlock_integration = TwistLockIntegration(instance)

        self.assertFalse(twistlock_integration.is_valid())

if __name__ == '__main__':
    unittest.main()
