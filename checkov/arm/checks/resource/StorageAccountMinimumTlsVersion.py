from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class StorageAccountMinimumTlsVersion(BaseResourceCheck):
    def __init__(self) -> None:
        """
            Looks for min_tls_version configuration at azurerm_storage_account to be set to TLS1_2
            https://www.terraform.io/docs/providers/azurerm/r/storage_account.html#min_tls_version
            :param conf: azurerm_storage_account configuration
            :return: <CheckResult>
        """
        name = "Ensure Storage Account is using the latest version of TLS encryption"
        id = "CKV_AZURE_44"
        supported_resources = ('Microsoft.Storage/storageAccounts',)
        categories = (CheckCategories.NETWORKING,)

        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf and \
            "minimumTlsVersion" in conf["properties"] and \
                conf["properties"]["minimumTlsVersion"] in ['TLS1_2']:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = StorageAccountMinimumTlsVersion()
