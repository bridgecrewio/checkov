from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class StorageSyncServicePermissiveAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Storage Sync Service is not configured with overly permissive network access"
        id = "CKV_AZURE_250"
        supported_resources = ['azurerm_storage_sync']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if "incoming_traffic_policy" in conf:
            if "AllowAllTraffic" in conf["incoming_traffic_policy"]:
                return CheckResult.FAILED
        else:
            return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['incoming_traffic_policy']


check = StorageSyncServicePermissiveAccess()
