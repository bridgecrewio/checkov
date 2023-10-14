from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from checkov.arm.registry import arm_resource_registry
from checkov.bicep.checks.resource.registry import registry as bicep_registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories, CheckResult


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
                # the existing keyword is used to retrieve information about an already deployed resource
                return CheckResult.UNKNOWN

            self.api_version = conf["api_version"]
            conf["config"]["apiVersion"] = conf["api_version"]  # set for better reusability of existing ARM checks

            resource_conf = conf["config"]
            if "loop_type" in resource_conf:
                # this means the whole resource block is surrounded by a for loop
                resource_conf = resource_conf["config"]

            return self.scan_resource_conf(resource_conf)

        self.api_version = None

        return self.scan_resource_conf(conf)

    @abstractmethod
    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        raise NotImplementedError()
