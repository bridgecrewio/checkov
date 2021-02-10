import os
from abc import ABC, abstractmethod

from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry


class BaseIntegrationFeature(ABC):
    bc_api_url = os.getenv('BC_API_URL', "https://www.bridgecrew.cloud/api/v1")
    integrations_api_url = f"{bc_api_url}/integrations/types/checkov"
    guidelines_api_url = f"{bc_api_url}/guidelines"
    onboarding_url = f"{bc_api_url}/signup/checkov"
    api_token_url = f"{bc_api_url}/integrations/apiToken"
    suppressions_url = f"{bc_api_url}/suppressions"
    fixes_url = f"{bc_api_url}/fixes/checkov"

    def __init__(self, bc_integration, order):
        self.bc_integration = bc_integration
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

