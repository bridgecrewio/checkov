from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class ACRGeoreplicated(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Container Registry resources are connected to their replications"
        id = "CKV_AZURE_165"
        supported_resources = ("Microsoft.ContainerRegistry/registries",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("properties", {})
        replications = properties.get("replications", [])
        if replications:
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


check = ACRGeoreplicated()


