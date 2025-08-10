from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class CosmosDBDisableAccessKeyWrite(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure cosmosdb does not allow privileged escalation by restricting management plane changes"
        id = "CKV_AZURE_132"
        supported_resources = ('Microsoft.DocumentDB/databaseAccounts',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if 'properties' in conf:
            if "disableKeyBasedMetadataWriteAccess" in conf['properties'] and conf['properties']['disableKeyBasedMetadataWriteAccess']:
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties", "properties/disableKeyBasedMetadataWriteAccess"]


check = CosmosDBDisableAccessKeyWrite()
