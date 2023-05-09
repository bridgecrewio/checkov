from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry

if TYPE_CHECKING:
    from argparse import Namespace
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


class BaseIntegrationFeature(ABC):
    def __init__(self, bc_integration: BcPlatformIntegration, order: int) -> None:
        self.bc_integration = bc_integration
        self.order = order
        integration_feature_registry.register(self)
        self.integration_feature_failures = False
        self.config: Namespace | None = None  # is set during pre_scan()

    @abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def pre_scan(self) -> None:
        """Runs before any runners"""
        pass

    @abstractmethod
    def pre_runner(self, runner: _BaseRunner) -> None:
        """Runs before each runner"""
        pass

    @abstractmethod
    def post_runner(self, scan_reports: Report) -> None:
        """Runs after each runner completes"""
        pass

    @abstractmethod
    def post_scan(self, merged_reports: list[Report]) -> Report | None:
        """Runs after all runners complete"""
        pass
