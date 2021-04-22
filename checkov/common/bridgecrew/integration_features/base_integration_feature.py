import os
from abc import ABC, abstractmethod

from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry

BC_API_URL = os.getenv('BC_API_URL', "https://www.bridgecrew.cloud/api/v1")

class BaseIntegrationFeature(ABC):
    integrations_api_url = f"{BC_API_URL}/integrations/types/checkov"
    guidelines_api_url = f"{BC_API_URL}/guidelines"
    onboarding_url = f"{BC_API_URL}/signup/checkov"
    api_token_url = f"{BC_API_URL}/integrations/apiToken"
    suppressions_url = f"{BC_API_URL}/suppressions"
    fixes_url = f"{BC_API_URL}/fixes/checkov"

    def __init__(self, bc_integration, order):
        self.bc_integration = bc_integration
        bc_integration.setup_http_manager()
        self.order = order
        integration_feature_registry.register(self)

    @abstractmethod
    def is_valid(self):
        raise NotImplementedError()

    def pre_scan(self):
        # overriding is optional
        pass

    def post_scan(self, scan_reports):
        # overriding is optional
        pass

