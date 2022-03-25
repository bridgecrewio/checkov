from abc import ABC, abstractmethod

from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


class BaseIntegrationFeature(ABC):
    def __init__(self, bc_integration: BcPlatformIntegration, order):
        self.bc_integration = bc_integration
        self.order = order
        integration_feature_registry.register(self)
        self.integration_feature_failures = False

    @abstractmethod
    def is_valid(self):
        raise NotImplementedError()

    def pre_scan(self):
        """Runs before any runners"""
        pass

    def pre_runner(self):
        """Runs before each runner"""
        pass

    def post_runner(self, scan_reports):
        """Runs after each runner completes"""
        pass
