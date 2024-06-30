from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CosmosDBLocalAuthDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        description = "Ensure that Local Authentication is disabled on CosmosDB"
        id = "CKV_AZURE_140"
        supported_resources = ('Microsoft.DocumentDB/databaseAccounts',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get("kind") == "GlobalDocumentDB":
            return super().scan_resource_conf(conf)
        return CheckResult.UNKNOWN

    def get_inspected_key(self) -> str:
        return "properties/disableLocalAuth"

    def get_expected_value(self) -> bool:
        return True


check = CosmosDBLocalAuthDisabled()
