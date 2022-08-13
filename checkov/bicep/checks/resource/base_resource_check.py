from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, TYPE_CHECKING

from checkov.bicep.checks.resource.registry import registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult

if TYPE_CHECKING:
    from pycep.typing import ResourceAttributes


class BaseResourceCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        guideline: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type="resource",
            guideline=guideline,
        )
        self.supported_resources = supported_resources
        registry.register(self)

    def scan_entity_conf(self, conf: ResourceAttributes, entity_type: str) -> CheckResult:  # type:ignore[override]  # it's ok
        if conf["existing"] is True:
            # the existing keyword is used to retrieve information about an already deployed resource
            return CheckResult.UNKNOWN

        self.entity_type = entity_type
        self.api_version = conf["api_version"]

        return self.scan_resource_conf(conf["config"])

    @abstractmethod
    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        raise NotImplementedError()
