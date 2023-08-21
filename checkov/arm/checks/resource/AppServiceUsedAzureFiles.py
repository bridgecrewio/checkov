from __future__ import annotations
from typing import Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceUsedAzureFiles(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that app services use Azure Files"
        id = "CKV_AZURE_88"
        supported_resources = ["Microsoft.Web/sites/config"]
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get('properties') and isinstance(conf.get('properties'), dict):
            properties = conf.get('properties')
            if properties.get("azureStorageAccounts") and isinstance(properties.get("azureStorageAccounts"), dict):
                azureStorageAccounts = properties.get("azureStorageAccounts")
                for account in azureStorageAccounts:
                    if isinstance(azureStorageAccounts[account], dict) and azureStorageAccounts[account]['type'] == "AzureFiles":
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = AppServiceUsedAzureFiles()
