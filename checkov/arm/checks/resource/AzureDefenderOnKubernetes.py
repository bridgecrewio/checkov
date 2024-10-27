from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureDefenderOnKubernetes(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Defender is set to On for Kubernetes"
        id = "CKV_AZURE_85"
        supported_resources = ("Microsoft.Security/pricings",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        return (
            CheckResult.PASSED
            if conf.get("name") != "KubernetesService" or str(conf["properties"]["pricingTier"]).lower() == "standard"
            else CheckResult.FAILED
        )

    def get_evaluated_keys(self) -> list[str]:
        return ["name", "pricingTier"]


check = AzureDefenderOnKubernetes()
