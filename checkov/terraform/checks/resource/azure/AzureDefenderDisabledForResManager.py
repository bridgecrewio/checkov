from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureDefenderDisabledForResManager(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Defender for cloud is set to On for Resource Manager"
        id = "CKV_AZURE_234"
        supported_resources = ("azurerm_security_center_subscription_pricing",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        return (
            CheckResult.FAILED
            if conf.get("resource_type", [""])[0].lower() == "arm" and conf.get("tier", [""])[0].lower() != "standard"
            else CheckResult.PASSED
        )

    def get_evaluated_keys(self) -> list[str]:
        return ["resource_type", "tier"]


check = AzureDefenderDisabledForResManager()
