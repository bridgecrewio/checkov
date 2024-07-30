from __future__ import annotations

from typing import Any, Dict

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureDefenderOnKeyVaults(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Defender is set to On for Key Vault"
        id = "CKV_AZURE_87"
        supported_resources = ("Microsoft.Security/pricings",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get('properties', {})
        pricing_tier = properties.get('pricingTier')
        name = conf.get('name', '')
        return (
            CheckResult.PASSED
            if pricing_tier == "Standard" and name == 'KeyVaults'
            else CheckResult.FAILED
        )

    def get_evaluated_keys(self) -> list[str]:
        return ["properties.pricingTier", "name"]


check = AzureDefenderOnKeyVaults()
