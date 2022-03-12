from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, Callable

from checkov.arm.registry import arm_resource_registry
from checkov.bicep.checks.resource.registry import registry as bicep_registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.multi_signature import multi_signature


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
        arm_resource_registry.register(self)
        # leverage ARM checks to use with bicep runner
        bicep_registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        # the "existing" key indicates a Bicep resource
        if "existing" in conf:
            if conf["existing"] is True:
                # an existing is used to retrieve information about an already deployed one
                return CheckResult.UNKNOWN

            self.api_version = conf["api_version"]

            return self.scan_resource_conf(conf["config"], entity_type)

        self.api_version = None

        return self.scan_resource_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_resource_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        raise NotImplementedError()

    @classmethod
    @scan_resource_conf.add_signature(args=["self", "conf"])
    def _scan_resource_conf_self_conf(cls, wrapped: Callable[..., CheckResult]) -> Callable[..., CheckResult]:
        def wrapper(self: BaseCheck, conf: dict[str, Any], entity_type: str | None = None) -> CheckResult:
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
