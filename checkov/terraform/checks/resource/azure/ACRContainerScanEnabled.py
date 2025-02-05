from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACRContainerScanEnabled(BaseResourceCheck):
    SKUS = {"Standard", "Premium"}  # noqa: CCE003  # a static attribute

    def __init__(self):
        name = "Enable vulnerability scanning for container images."
        id = "CKV_AZURE_163"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # 'ContainerRegistry' tier
        # 'standard', or higher -
        # not Basic
        if (
            "sku" in conf.keys()
            and isinstance(conf["sku"][0], str)
            and conf["sku"][0] in ACRContainerScanEnabled.SKUS
        ):
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["sku"]


check = ACRContainerScanEnabled()
