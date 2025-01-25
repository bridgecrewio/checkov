from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class SecurityCenterStandardPricing(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.security/securitycontacts
        name = "Ensure that standard pricing tier is selected"
        id = "CKV_AZURE_19"
        supported_resources = ('Microsoft.Security/pricings',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["properties"]
        if "properties" in conf:
            if "pricingTier" in conf["properties"]:
                self.evaluated_keys = ["properties/pricingTier"]
                if str(conf["properties"]["pricingTier"]).lower() == "standard":
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = SecurityCenterStandardPricing()
