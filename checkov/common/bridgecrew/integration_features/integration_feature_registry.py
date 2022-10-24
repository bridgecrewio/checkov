from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from checkov.common.bridgecrew.integration_features.integration_feature_enum import IntegrationFeature

if TYPE_CHECKING:
    from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
    from checkov.common.output.report import Report


class IntegrationFeatureRegistry:
    __integrations_order__ = {
        IntegrationFeature.POLICY_METADATA: 0,
        IntegrationFeature.REPO_CONFIG: 0,
        IntegrationFeature.CUSTOM_POLICIES: 1,  # must be after policy metadata and before suppression integration
        IntegrationFeature.SUPPRESSIONS: 2,  # must be after the custom policies integration
        IntegrationFeature.FIXES: 10
    }

    def __init__(self) -> None:
        self.features: list[BaseIntegrationFeature] = []

    def register(self, integration_feature: BaseIntegrationFeature) -> None:
        logging.debug(f"Adding the IntegrationFeatureRegistry {integration_feature}")
        self.features.append(integration_feature)
        self.features.sort(key=lambda f: self.__integrations_order__.get(f.integration_name, 20))
        logging.debug("self.features after the sort:")
        logging.debug(self.features)

    def run_pre_scan(self) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.pre_scan()

    def run_pre_runner(self) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.pre_runner()

    def run_post_runner(self, scan_report: Report) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.post_runner(scan_report)


integration_feature_registry = IntegrationFeatureRegistry()
