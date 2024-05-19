from __future__ import annotations
from typing import List, Any, Dict
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureDefenderOnStorage(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Azure Defender is set to On for Storage"
        id = "CKV_AZURE_84"
        supported_resources = ("Microsoft.Security/pricings",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties: Dict[str, Any] = conf.get("properties", {})
        pricingTier = properties.get("pricingTier", "")
        resourceType = properties.get("resourceType", "")
        return (
            CheckResult.PASSED
            if resourceType != "Microsoft.Security/pricings" or pricingTier == "Standard"
            else CheckResult.FAILED
        )

    def get_evaluated_keys(self) -> List[str]:
        return ["properties/pricingTier", "properties/resourceType"]


check = AzureDefenderOnStorage()
