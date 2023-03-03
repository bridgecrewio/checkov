import unittest

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as policy_metadata_integration
from checkov.common.bridgecrew.integration_features.features.custom_policies_integration import integration as custom_policies_integration
from checkov.common.bridgecrew.integration_features.features.fixes_integration import integration as fixes_integration
from checkov.common.bridgecrew.integration_features.features.repo_config_integration import integration as repo_config_integration
from checkov.common.bridgecrew.integration_features.features.suppressions_integration import integration as suppressions_integration


class TestSuppressionsIntegration(unittest.TestCase):
    def test_feature_order(self):
        self.assertGreater(fixes_integration.order, max([i.order for i in [policy_metadata_integration, custom_policies_integration, repo_config_integration, suppressions_integration]]))
        self.assertGreater(custom_policies_integration.order, policy_metadata_integration.order)
        self.assertGreater(suppressions_integration.order, policy_metadata_integration.order)


if __name__ == '__main__':
    unittest.main()
