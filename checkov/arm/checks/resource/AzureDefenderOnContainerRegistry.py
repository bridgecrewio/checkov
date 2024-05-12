from __future__ import annotations

from typing import List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureDefenderOnContainerRegistry(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Defender is set to On for Container Registries"
        id = "CKV_AZURE_86"
        supported_resources = ("Microsoft.ContainerRegistry/registries",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        properties = conf.get("properties", {})

        tier = properties.get("tier")

        resourceType = properties.get("resourceType")

        return (

            CheckResult.PASSED

            if resourceType != "ContainerRegistry" or tier == "Standard"

            else CheckResult.FAILED
        )

    def get_evaluated_keys(self) -> List[str]:
        return ["properties/tier", "properties/resourceType"]


check = AzureDefenderOnContainerRegistry()
