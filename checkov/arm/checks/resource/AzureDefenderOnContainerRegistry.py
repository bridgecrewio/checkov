from __future__ import annotations

from typing import List

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult

class AzureDefenderOnContainerRegistry(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Defender is set to On for Container Registries"
        id = "CKV_AZURE_86"
        supported_resources = ("Microsoft.Security/pricings",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        properties = conf.get("properties", {})

        pricingTier = properties.get("pricingTier")

        type = properties.get("type")

        return (

            CheckResult.PASSED

            if type != "ContainerRegistry" or pricingTier == "Standard"

            else CheckResult.FAILED
        )

    def get_evaluated_keys(self) -> List[str]:
        return ["properties/pricingTier	", "properties/type"]


check = AzureDefenderOnContainerRegistry()
