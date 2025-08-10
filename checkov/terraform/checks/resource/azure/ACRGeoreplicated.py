from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ACRGeoreplicated(BaseResourceCheck):
    def __init__(self) -> None:
        # Check to see the sku is set to premium with any replication block set

        name = "Ensure geo-replicated container registries to match multi-region container deployments."
        id = "CKV_AZURE_165"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        sku = conf.get("sku")
        if sku == ["Premium"]:
            replication = conf.get("georeplications")
            if replication:
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['sku', 'georeplications']


check = ACRGeoreplicated()
