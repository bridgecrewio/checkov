from __future__ import annotations

from abc import abstractmethod
from typing import Iterable, Any, TYPE_CHECKING

from checkov.common.checks.base_check import BaseCheck
from checkov.serverless.checks.plugin.registry import plugin_registry

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories, CheckResult


class BasePluginCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_entities: Iterable[str],
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type="serverless",
            guideline=guideline,
        )
        plugin_registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        return self.scan_plugin_list(conf)

    @abstractmethod
    def scan_plugin_list(self, plugin_list: dict[str, Any]) -> CheckResult:
        raise NotImplementedError()
