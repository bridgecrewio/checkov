from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureDefenderDisabledForResManager(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Defender for cloud is set to On for Resource Manager"
        id = "CKV_AZURE_234"
        supported_resources = ("Microsoft.Security/pricings",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "properties" in conf:
            if "pricingTier" in conf["properties"]:
                if str(conf["properties"]["pricingTier"]).lower() != "standard":
                    if str(conf["properties"]["resourceType"]).lower() == "arm":
                        return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["resourceType", "pricingTier"]


check = AzureDefenderDisabledForResManager()
