from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


class IntegrationFeatureRegistry:
    def __init__(self) -> None:
        self.features: list[BaseIntegrationFeature] = []

    def register(self, integration_feature: BaseIntegrationFeature) -> None:
        logging.debug(f"Adding the IntegrationFeatureRegistry {integration_feature} with order {integration_feature.order}")
        self.features.append(integration_feature)
        self.features.sort(key=lambda f: f.order)
        logging.debug("self.features after the sort:")
        logging.debug(self.features)

    def run_pre_scan(self) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.pre_scan()

    def run_pre_runner(self, runner: _BaseRunner) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.pre_runner(runner)

    def run_post_runner(self, scan_report: Report) -> None:
        for integration in self.features:
            if integration.is_valid():
                integration.post_runner(scan_report)

    def run_post_scan(self, scan_reports: list[Report]) -> list[Report]:
        post_scan_reports = []
        for integration in self.features:
            if integration.is_valid():
                integration_report = integration.post_scan(scan_reports)
                if integration_report:
                    post_scan_reports.append(integration_report)

        return post_scan_reports


integration_feature_registry = IntegrationFeatureRegistry()
